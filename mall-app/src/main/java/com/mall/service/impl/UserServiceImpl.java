package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.JwtUtil;
import com.mall.common.UserBalanceUtil;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.entity.Kyc;
import com.mall.mapper.*;
import com.mall.service.GoogleAuthService;
import com.mall.service.IdcodeService;
import com.mall.service.SysParamService;
import com.mall.service.UserService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private static final Logger auditLog = LoggerFactory.getLogger("AUDIT");

    private final UserMapper userMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final UserSafewordApplyMapper safewordApplyMapper;
    private final KycMapper kycMapper;
    private final MallComplaintMapper complaintMapper;
    private final WithdrawOrderMapper withdrawOrderMapper;
    private final RechargeOrderMapper rechargeOrderMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final IdcodeService idcodeService;
    private final GoogleAuthService googleAuthService;
    private final SysParamService sysParamService;
    private final RedisTemplate<String, Object> redisTemplate;

    @Override
    public Map<String, Object> login(String account, String password, String ip) {
        // Redis rate limiting — same day-lockout pattern as verifySafeword
        String ipKey = "mall:login:fail:ip:" + ip;
        String accountKey = "mall:login:fail:account:" + account;
        Integer ipFails = (Integer) redisTemplate.opsForValue().get(ipKey);
        Integer acctFails = (Integer) redisTemplate.opsForValue().get(accountKey);
        long secondsUntilMidnight = ChronoUnit.SECONDS.between(
            LocalDateTime.now(), LocalDateTime.of(LocalDate.now().plusDays(1), LocalTime.MIDNIGHT));
        if (ipFails != null && ipFails >= 10)
            throw new BizException("登录尝试过于频繁，请明天再试");
        if (acctFails != null && acctFails >= 5)
            throw new BizException("该账号登录错误次数过多，请明天再试");

        // account can be email or phone — check both
        User user = userMapper.selectOne(new QueryWrapper<User>()
            .eq("deleted", 0)
            .and(w -> w.eq("phone", account).or().eq("email", account)));
        if (user == null) {
            incrementFail(ipKey, ipFails, secondsUntilMidnight);
            auditLog.warn("LOGIN_FAIL account={} ip={} reason=account_not_found", account, ip);
            throw new BizException("账号不存在");
        }
        if (user.getStatus() == 1) {
            auditLog.warn("LOGIN_FAIL account={} ip={} reason=account_disabled", account, ip);
            throw new BizException("账号已被禁用");
        }
        if (!passwordEncoder.matches(password, user.getPassword())) {
            incrementFail(ipKey, ipFails, secondsUntilMidnight);
            incrementFail(accountKey, acctFails, secondsUntilMidnight);
            auditLog.warn("LOGIN_FAIL account={} ip={} reason=wrong_password", account, ip);
            throw new BizException("密码错误");
        }

        // login success — clear fail counters
        redisTemplate.delete(ipKey);
        redisTemplate.delete(accountKey);
        auditLog.info("LOGIN_SUCCESS userId={} account={} ip={}", user.getId(), account, ip);

        String token = jwtUtil.generateToken(user.getId(), "USER");
        return Map.of("token", token, "userInfo", toSafeUserMap(user));
    }

    private void incrementFail(String ipKey, Integer currentFails, long ttlSeconds) {
        if (currentFails == null) {
            redisTemplate.opsForValue().set(ipKey, 1, Duration.ofSeconds(ttlSeconds));
        } else {
            redisTemplate.opsForValue().increment(ipKey);
            redisTemplate.expire(ipKey, Duration.ofSeconds(ttlSeconds));
        }
    }

    @Override
    public void register(String email, String phone, String password) {
        validatePasswordStrength(password);
        User exist = userMapper.selectOne(new QueryWrapper<User>().eq("phone", phone));
        if (exist != null) throw new BizException("手机号已被注册");
        if (email != null && !email.isBlank()) {
            exist = userMapper.selectOne(new QueryWrapper<User>().eq("email", email));
            if (exist != null) throw new BizException("邮箱已被注册");
        }

        User user = User.builder().phone(phone)
            .email(email)
            .password(passwordEncoder.encode(password))
            .nickname("用户" + phone.substring(phone.length() - 4))
            .status(0).levelId(1).build();
        userMapper.insert(user);

        UserBalance balance = UserBalance.builder()
            .userId(user.getId()).balance(java.math.BigDecimal.ZERO)
            .frozen(java.math.BigDecimal.ZERO).version(0).build();
        userBalanceMapper.insert(balance);

        auditLog.info("REGISTER_SUCCESS userId={} phone={} email={}", user.getId(), phone, email);
    }

    @Override
    public Object getInfo(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        return toSafeUserMap(user);
    }

    @Override
    public void resetPasswordSendCode(String phone, String ip) {
        User user = userMapper.selectOne(new QueryWrapper<User>().eq("phone", phone).eq("deleted", 0));
        if (user == null) throw new BizException("该手机号未注册");
        if (user.getStatus() == 1) throw new BizException("账号已被禁用");
        idcodeService.send(phone, "RESET_PWD", ip);
    }

    @Override
    @Transactional
    public void resetPassword(String phone, String code, String newPassword) {
        validatePasswordStrength(newPassword);
        boolean ok = idcodeService.verify(phone, code, "RESET_PWD");
        if (!ok) throw new BizException("验证码校验失败");

        User user = userMapper.selectOne(new QueryWrapper<User>().eq("phone", phone).eq("deleted", 0));
        if (user == null) throw new BizException("用户不存在");

        userMapper.update(null,
            new UpdateWrapper<User>()
                .eq("id", user.getId())
                .set("password", passwordEncoder.encode(newPassword)));
        auditLog.warn("RESET_PASSWORD userId={}", user.getId());

        // 吊销该用户所有旧Token
        jwtUtil.revokeUserTokens(user.getId());
    }

    @Override
    public Object getBalance(Long userId) {
        UserBalance ub = userBalanceMapper.selectOne(new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (ub == null) return Map.of("balance", 0, "frozen", 0, "available", 0);
        java.math.BigDecimal available = UserBalanceUtil.getAvailable(ub);
        return Map.of("balance", ub.getBalance(), "frozen", ub.getFrozen(), "available", available);
    }

    @Override
    public Map<String, Object> getVerifyMethods(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        return Map.of(
            "google_auth_bind", user.getGoogleAuthSecret() != null && !user.getGoogleAuthSecret().isEmpty(),
            "phone_authority", user.getPhone() != null && !user.getPhone().isEmpty(),
            "email_authority", user.getEmail() != null && !user.getEmail().isEmpty(),
            "safeword_set", user.getSafeword() != null && !user.getSafeword().isEmpty()
        );
    }

    @Override
    public Map<String, Object> getGoogleAuth(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        if (user.getGoogleAuthSecret() != null && !user.getGoogleAuthSecret().isEmpty()) {
            return Map.of("bound", true);
        }
        Map<String, String> data = googleAuthService.generateSecret(user.getEmail());
        return Map.of("bound", false, "google_auth_secret", data.get("secret"), "google_auth_url", data.get("qrUrl"));
    }

    @Override
    public boolean bindGoogleAuth(Long userId, String secret, int code) {
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        if (secret == null || secret.isEmpty()) throw new BizException("请先获取谷歌验证器密钥");
        boolean ok = googleAuthService.verifyCode(secret, code);
        if (!ok) throw new BizException("谷歌验证码错误");
        user.setGoogleAuthSecret(secret);
        userMapper.updateById(user);
        return true;
    }

    @Override
    public boolean verifySafeword(Long userId, String safeword) {
        // 从系统参数读取最大错误次数，默认5次
        int maxFail = 5;
        try {
            String maxFailStr = sysParamService.getString("number_of_wrong_passwords");
            if (maxFailStr != null && !maxFailStr.isEmpty()) {
                maxFail = Integer.parseInt(maxFailStr);
            }
        } catch (Exception ignored) {}

        String lockKey = "mall:safeword:fail:" + userId;
        Integer failCount = (Integer) redisTemplate.opsForValue().get(lockKey);
        if (failCount != null && failCount >= maxFail) {
            throw new BizException("资金密码错误次数过多，请明天再试");
        }

        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        if (user.getSafeword() == null || user.getSafeword().isEmpty()) {
            throw new BizException("未设置资金密码");
        }

        boolean ok = passwordEncoder.matches(safeword, user.getSafeword());
        if (!ok) {
            // 锁到第二天凌晨 (old mall behavior: day-based lockout)
            long secondsUntilMidnight = ChronoUnit.SECONDS.between(
                LocalDateTime.now(), LocalDateTime.of(LocalDate.now().plusDays(1), LocalTime.MIDNIGHT));
            if (failCount == null) {
                redisTemplate.opsForValue().set(lockKey, 1, Duration.ofSeconds(secondsUntilMidnight));
            } else {
                redisTemplate.opsForValue().increment(lockKey);
                // 续期到明天凌晨
                redisTemplate.expire(lockKey, Duration.ofSeconds(secondsUntilMidnight));
            }
            return false;
        }
        // 验证成功，清除失败计数
        redisTemplate.delete(lockKey);
        return true;
    }

    @Override
    @Transactional
    public void setSafeword(Long userId, String oldSafeword, String safeword, String reSafeword) {
        if (safeword == null || safeword.length() != 6 || !safeword.matches("\\d{6}")) {
            throw new BizException("资金密码必须是6位数字");
        }
        if (!safeword.equals(reSafeword)) {
            throw new BizException("两次输入的密码不一致");
        }
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");

        if (user.getSafeword() != null && !user.getSafeword().isEmpty()) {
            if (oldSafeword == null || oldSafeword.isEmpty()) {
                throw new BizException("请输入原资金密码");
            }
            if (!passwordEncoder.matches(oldSafeword, user.getSafeword())) {
                throw new BizException("原资金密码错误");
            }
        }
        user.setSafeword(passwordEncoder.encode(safeword));
        userMapper.updateById(user);
        auditLog.warn("SET_SAFEWORD userId={}", userId);
    }

    @Override
    @Transactional
    public void changePassword(Long userId, String oldPassword, String newPassword) {
        validatePasswordStrength(newPassword);
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        if (!passwordEncoder.matches(oldPassword, user.getPassword()))
            throw new BizException("原密码错误");
        userMapper.update(null,
            new UpdateWrapper<User>().eq("id", userId)
                .set("password", passwordEncoder.encode(newPassword)));
        auditLog.warn("CHANGE_PASSWORD userId={}", userId);

        // 吊销该用户所有旧Token，强制重新登录
        jwtUtil.revokeUserTokens(userId);
    }

    @Override
    public void bindSendCode(Long userId, String target, String type, String ip) {
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        if (!"phone".equals(type) && !"email".equals(type)) {
            throw new BizException("绑定类型不正确");
        }
        // 检查目标是否已被其他用户绑定
        User exist = userMapper.selectOne(new QueryWrapper<User>()
            .eq(type, target).eq("deleted", 0).ne("id", userId));
        if (exist != null) throw new BizException(type.equals("phone") ? "该手机号已被其他用户绑定" : "该邮箱已被其他用户绑定");
        idcodeService.send(target, "BIND_" + type.toUpperCase(), ip);
    }

    @Override
    @Transactional
    public void bindPhone(Long userId, String phone, String code, String loginPassword) {
        if (phone == null || phone.isBlank()) throw new BizException("手机号不能为空");
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");

        // 换绑（已有手机号）需要验证登录密码
        if (user.getPhone() != null && !user.getPhone().isEmpty()) {
            if (loginPassword == null || loginPassword.isEmpty())
                throw new BizException("修改已绑定手机号需要验证登录密码");
            if (!passwordEncoder.matches(loginPassword, user.getPassword()))
                throw new BizException("登录密码错误");
        }

        boolean ok = idcodeService.verify(phone, code, "BIND_PHONE");
        if (!ok) throw new BizException("验证码校验失败");

        User exist = userMapper.selectOne(new QueryWrapper<User>()
            .eq("phone", phone).eq("deleted", 0).ne("id", userId));
        if (exist != null) throw new BizException("该手机号已被其他用户绑定");

        userMapper.update(null,
            new UpdateWrapper<User>().eq("id", userId).set("phone", phone));
        auditLog.warn("BIND_PHONE userId={} phone={}", userId, phone);
    }

    @Override
    @Transactional
    public void bindEmail(Long userId, String email, String code, String loginPassword) {
        if (email == null || email.isBlank()) throw new BizException("邮箱不能为空");
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");

        // 换绑（已有邮箱）需要验证登录密码
        if (user.getEmail() != null && !user.getEmail().isEmpty()) {
            if (loginPassword == null || loginPassword.isEmpty())
                throw new BizException("修改已绑定邮箱需要验证登录密码");
            if (!passwordEncoder.matches(loginPassword, user.getPassword()))
                throw new BizException("登录密码错误");
        }

        boolean ok = idcodeService.verify(email, code, "BIND_EMAIL");
        if (!ok) throw new BizException("验证码校验失败");

        User exist = userMapper.selectOne(new QueryWrapper<User>()
            .eq("email", email).eq("deleted", 0).ne("id", userId));
        if (exist != null) throw new BizException("该邮箱已被其他用户绑定");

        userMapper.update(null,
            new UpdateWrapper<User>().eq("id", userId).set("email", email));
        auditLog.warn("BIND_EMAIL userId={} email={}", userId, email);
    }

    @Override
    @Transactional
    public void applySafewordReset(Long userId, String safeword, String reSafeword, Integer operate,
                                   String idcardFront, String idcardBack, String idcardHold, String remark) {
        if (operate == null || operate < 0 || operate > 3) throw new BizException("操作类型不正确");

        // KYC实名认证校验（老商城要求：实名认证通过才能人工重置）
        Kyc kyc = kycMapper.selectOne(new QueryWrapper<Kyc>().eq("user_id", userId));
        if (kyc == null || kyc.getStatus() == null || kyc.getStatus() != 1) {
            throw new BizException("实名认证尚未通过，无法提交重置申请");
        }

        if (operate == 0) {
            if (safeword == null || safeword.length() != 6 || !safeword.matches("\\d{6}")) {
                throw new BizException("资金密码必须是6位数字");
            }
            if (!safeword.equals(reSafeword)) throw new BizException("两次输入的密码不一致");
        }

        // 检查是否有待处理的同类型申请
        Long pending = safewordApplyMapper.selectCount(new QueryWrapper<UserSafewordApply>()
            .eq("user_id", userId).eq("operate", operate).eq("status", 1));
        if (pending > 0) throw new BizException("您有一笔待处理的申请，请勿重复提交");

        UserSafewordApply apply = UserSafewordApply.builder()
            .userId(userId)
            .safeword(operate == 0 ? passwordEncoder.encode(safeword) : null)
            .operate(operate)
            .status(1)
            .idcardPathFront(idcardFront)
            .idcardPathBack(idcardBack)
            .idcardPathHold(idcardHold)
            .remark(remark)
            .build();
        safewordApplyMapper.insert(apply);
    }

    @Override
    public List<Map<String, Object>> getMySafewordApplies(Long userId) {
        List<UserSafewordApply> list = safewordApplyMapper.selectList(
            new QueryWrapper<UserSafewordApply>()
                .eq("user_id", userId)
                .orderByDesc("create_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (UserSafewordApply a : list) {
            Map<String, Object> m = Map.of(
                "id", a.getId(),
                "operate", a.getOperate(),
                "status", a.getStatus(),
                "msg", a.getMsg() != null ? a.getMsg() : "",
                "remark", a.getRemark() != null ? a.getRemark() : "",
                "create_time", a.getCreateTime() != null ? a.getCreateTime().toString() : "",
                "apply_time", a.getApplyTime() != null ? a.getApplyTime().toString() : ""
            );
            result.add(m);
        }
        return result;
    }

    // ==================== Complaint ====================

    @Override
    public void submitComplaint(Long userId, String type, String reason, String images) {
        if (type == null || type.isBlank()) throw new BizException("请选择投诉类型");
        if (reason == null || reason.isBlank()) throw new BizException("请输入投诉原因");
        MallComplaint c = new MallComplaint();
        c.setUserId(userId);
        c.setType(type);
        c.setReason(reason);
        c.setImages(images);
        c.setStatus(1);
        complaintMapper.insert(c);
    }

    @Override
    public List<Map<String, Object>> complaintList(Long userId, Integer pageNum, Integer pageSize) {
        int p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        int ps = pageSize == null || pageSize < 1 ? 10 : pageSize;
        IPage<MallComplaint> page = complaintMapper.selectPage(new Page<>(p, ps),
            new QueryWrapper<MallComplaint>().eq("user_id", userId).orderByDesc("create_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallComplaint c : page.getRecords()) {
            result.add(Map.of("id", c.getId(), "type", c.getType(),
                "reason", c.getReason(), "images", c.getImages() != null ? c.getImages() : "",
                "status", c.getStatus(), "createTime", c.getCreateTime() != null ? c.getCreateTime().toString() : ""));
        }
        return result;
    }

    // ==================== Logoff ====================

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void logoff(Long userId, String reason, String cashPassword) {
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");

        // Verify safeword if set
        if (user.getSafeword() != null && !user.getSafeword().isEmpty()) {
            if (cashPassword == null || cashPassword.isEmpty())
                throw new BizException("请输入资金密码");
            if (!passwordEncoder.matches(cashPassword, user.getSafeword()))
                throw new BizException("资金密码错误");
        }

        // Check unfinished withdraws
        Long unfinishedWithdraws = withdrawOrderMapper.selectCount(
            new QueryWrapper<WithdrawOrder>().eq("user_id", userId).eq("status", 0));
        if (unfinishedWithdraws > 0) throw new BizException("有未完成的提现订单，请先处理");

        // Check unfinished recharges
        Long unfinishedRecharges = rechargeOrderMapper.selectCount(
            new QueryWrapper<RechargeOrder>().eq("user_id", userId).eq("status", 0));
        if (unfinishedRecharges > 0) throw new BizException("有未完成的充值订单，请先处理");

        // Check non-zero available balance
        UserBalance ub = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (ub != null) {
            BigDecimal available = UserBalanceUtil.getAvailable(ub);
            if (available.compareTo(BigDecimal.ZERO) != 0)
                throw new BizException("账户还有可用余额，请先提现全部余额后再注销");
        }

        // Soft delete: @TableLogic marks deleted=1
        userMapper.deleteById(userId);
        auditLog.warn("LOGOFF userId={} reason={}", userId, reason);

        // 吊销该用户所有Token
        jwtUtil.revokeUserTokens(userId);
    }

    @Override
    public Map<String, String> getImageCode() {
        String text = String.format("%04d", new java.util.Random().nextInt(10000));
        java.awt.image.BufferedImage img = new java.awt.image.BufferedImage(120, 40, java.awt.image.BufferedImage.TYPE_INT_RGB);
        java.awt.Graphics2D g = img.createGraphics();
        g.setColor(java.awt.Color.WHITE);
        g.fillRect(0, 0, 120, 40);
        g.setColor(java.awt.Color.BLACK);
        g.setFont(new java.awt.Font("Arial", java.awt.Font.BOLD, 24));
        g.drawString(text, 20, 30);
        g.dispose();
        java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
        try {
            javax.imageio.ImageIO.write(img, "png", bos);
        } catch (java.io.IOException e) {
            throw new BizException("生成验证码失败");
        }
        String base64 = java.util.Base64.getEncoder().encodeToString(bos.toByteArray());
        String key = java.util.UUID.randomUUID().toString().replace("-", "");
        redisTemplate.opsForValue().set("mall:imageCode:" + key, text, Duration.ofMinutes(5));
        return Map.of("code", "data:image/png;base64," + base64, "key", key);
    }

    @Override
    public Map<String, Object> getShare(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        return Map.of(
            "username", user.getPhone() != null ? user.getPhone() : user.getEmail(),
            "usercode", String.valueOf(user.getId()),
            "userLevel", user.getLevelId() != null ? user.getLevelId() : 1,
            "avatar", user.getAvatar() != null ? user.getAvatar() : "1"
        );
    }

    @Override
    public void refreshAvatar(Long userId, Integer idx) {
        User user = userMapper.selectById(userId);
        if (user == null) throw new BizException("用户不存在");
        userMapper.update(null,
            new UpdateWrapper<User>().eq("id", userId).set("avatar", String.valueOf(idx)));
    }

    // ==================== Helpers ====================

    private Map<String, Object> toSafeUserMap(User user) {
        user.setPassword(null);
        user.setGoogleAuthSecret(null);
        user.setSafeword(null);
        return Map.of(
            "id", user.getId(),
            "phone", user.getPhone() != null ? user.getPhone() : "",
            "email", user.getEmail() != null ? user.getEmail() : "",
            "nickname", user.getNickname() != null ? user.getNickname() : "",
            "avatar", user.getAvatar() != null ? user.getAvatar() : "",
            "status", user.getStatus(),
            "levelId", user.getLevelId() != null ? user.getLevelId() : 1,
            "createTime", user.getCreateTime() != null ? user.getCreateTime().toString() : ""
        );
    }

    private void validatePasswordStrength(String password) {
        if (password == null || password.length() < 6) {
            throw new BizException("密码至少6位");
        }
        if (!password.matches(".*[a-zA-Z].*") || !password.matches(".*\\d.*")) {
            throw new BizException("密码需包含字母和数字");
        }
    }
}
