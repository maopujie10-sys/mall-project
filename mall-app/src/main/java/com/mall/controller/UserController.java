package com.mall.controller;

import com.mall.common.JwtUtil;
import com.mall.common.Result;
import com.mall.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    private final JwtUtil jwtUtil;

    @PostMapping("/login")
    public Result<?> login(@RequestBody Map<String, String> dto, HttpServletRequest request) {
        String account = dto.get("account");
        if (account == null || account.isBlank()) account = dto.get("phone");
        if (account == null || account.isBlank()) account = dto.get("email");
        if (account == null || account.isBlank()) return Result.fail("请输入邮箱或手机号");
        return Result.ok(userService.login(account, dto.get("password"), request.getRemoteAddr()));
    }

    @PostMapping("/register")
    public Result<?> register(@RequestBody Map<String, String> dto) {
        String phone = dto.get("phone");
        if (phone == null || phone.isBlank()) return Result.fail("手机号不能为空");
        userService.register(dto.get("email"), phone, dto.get("password"));
        return Result.ok();
    }

    @GetMapping("/info")
    public Result<?> info(@RequestAttribute Long userId) {
        return Result.ok(userService.getInfo(userId));
    }

    @GetMapping("/balance")
    public Result<?> balance(@RequestAttribute Long userId) {
        return Result.ok(userService.getBalance(userId));
    }

    @PostMapping("/reset-password/send-code")
    public Result<?> resetPasswordSendCode(@RequestBody Map<String, String> body,
                                           HttpServletRequest request) {
        String phone = body.get("phone");
        if (phone == null || phone.isEmpty()) {
            return Result.fail("手机号不能为空");
        }
        userService.resetPasswordSendCode(phone, request.getRemoteAddr());
        return Result.ok();
    }

    @PostMapping("/reset-password")
    public Result<?> resetPassword(@RequestBody Map<String, String> body) {
        String phone = body.get("phone");
        String code = body.get("code");
        String newPassword = body.get("newPassword");
        if (phone == null || phone.isEmpty()) return Result.fail("手机号不能为空");
        if (code == null || code.isEmpty()) return Result.fail("验证码不能为空");
        if (newPassword == null || newPassword.isEmpty()) return Result.fail("新密码不能为空");
        userService.resetPassword(phone, code, newPassword);
        return Result.ok();
    }

    /** 修改登录密码（登录后使用，需验证原密码） */
    @PostMapping("/change-password")
    public Result<?> changePassword(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String oldPassword = body.get("oldPassword");
        String newPassword = body.get("newPassword");
        if (oldPassword == null || oldPassword.isEmpty()) return Result.fail("原密码不能为空");
        if (newPassword == null || newPassword.isEmpty()) return Result.fail("新密码不能为空");
        userService.changePassword(userId, oldPassword, newPassword);
        return Result.ok();
    }

    // ==================== 安全模块（窗口3） ====================

    /** 获取用户安全验证方式绑定状态 */
    @GetMapping("/verify-methods")
    public Result<?> verifyMethods(@RequestAttribute Long userId) {
        return Result.ok(userService.getVerifyMethods(userId));
    }

    /** 获取谷歌验证器绑定信息（QR+密钥） */
    @GetMapping("/google-auth")
    public Result<?> getGoogleAuth(@RequestAttribute Long userId) {
        return Result.ok(userService.getGoogleAuth(userId));
    }

    /** 绑定谷歌验证器 */
    @PostMapping("/google-auth")
    public Result<?> bindGoogleAuth(@RequestAttribute Long userId, @RequestBody Map<String, Object> body) {
        String secret = (String) body.get("secret");
        int code = Integer.parseInt(body.get("code").toString());
        boolean ok = userService.bindGoogleAuth(userId, secret, code);
        return Result.ok(Map.of("google_auth_bind", ok));
    }

    /** 设置/修改资金密码 */
    @PostMapping("/safeword")
    public Result<?> setSafeword(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String oldSafeword = body.get("old_safeword");
        String safeword = body.get("safeword");
        String reSafeword = body.get("re_safeword");
        if (safeword == null || safeword.isEmpty()) return Result.fail("资金密码不能为空");
        userService.setSafeword(userId, oldSafeword, safeword, reSafeword);
        return Result.ok();
    }

    /** 验证资金密码（下单/提现时二次验证，含Redis限流） */
    @PostMapping("/safeword/verify")
    public Result<?> verifySafeword(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String safeword = body.get("safeword");
        if (safeword == null || safeword.isEmpty()) return Result.fail("资金密码不能为空");
        boolean valid = userService.verifySafeword(userId, safeword);
        return Result.ok(Map.of("valid", valid));
    }

    // ==================== 手机/邮箱绑定（窗口3） ====================

    /** 发送绑定验证码 */
    @PostMapping("/bind/send-code")
    public Result<?> bindSendCode(@RequestAttribute Long userId, @RequestBody Map<String, String> body,
                                  HttpServletRequest request) {
        String target = body.get("target");
        String type = body.get("type");  // "phone" or "email"
        if (target == null || target.isEmpty()) return Result.fail("手机号/邮箱不能为空");
        if (type == null || (!type.equals("phone") && !type.equals("email")))
            return Result.fail("绑定类型必须是phone或email");
        userService.bindSendCode(userId, target, type, request.getRemoteAddr());
        return Result.ok();
    }

    /** 绑定/换绑手机号（已有手机号时需传loginPassword验证身份） */
    @PostMapping("/bind/phone")
    public Result<?> bindPhone(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String phone = body.get("phone");
        String code = body.get("code");
        String loginPassword = body.get("loginPassword");
        if (phone == null || phone.isEmpty()) return Result.fail("手机号不能为空");
        if (code == null || code.isEmpty()) return Result.fail("验证码不能为空");
        userService.bindPhone(userId, phone, code, loginPassword);
        return Result.ok();
    }

    /** 绑定/换绑邮箱（已有邮箱时需传loginPassword验证身份） */
    @PostMapping("/bind/email")
    public Result<?> bindEmail(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String email = body.get("email");
        String code = body.get("code");
        String loginPassword = body.get("loginPassword");
        if (email == null || email.isEmpty()) return Result.fail("邮箱不能为空");
        if (code == null || code.isEmpty()) return Result.fail("验证码不能为空");
        userService.bindEmail(userId, email, code, loginPassword);
        return Result.ok();
    }

    // ==================== 人工重置申请（窗口3） ====================

    /** 获取用户自己的安全重置申请列表 */
    @GetMapping("/safeword/apply/list")
    public Result<?> getMySafewordApplies(@RequestAttribute Long userId) {
        return Result.ok(userService.getMySafewordApplies(userId));
    }

    /** 提交安全重置申请（资金密码/谷歌/手机/邮箱） */
    @PostMapping("/safeword/apply")
    public Result<?> applySafewordReset(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String safeword = body.get("safeword");
        String reSafeword = body.get("re_safeword");
        String operateStr = body.get("operate");
        if (operateStr == null) return Result.fail("操作类型不能为空");
        int operate = Integer.parseInt(operateStr);
        if (operate == 0 && (safeword == null || safeword.isEmpty()))
            return Result.fail("新资金密码不能为空");

        userService.applySafewordReset(userId, safeword, reSafeword, operate,
            body.get("idcardFront"), body.get("idcardBack"), body.get("idcardHold"),
            body.get("remark"));
        return Result.ok();
    }

    /** 账号注销 */
    @PostMapping("/logoff")
    public Result<?> logoff(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String reason = body.get("reason");
        String cashPassword = body.get("cashPassword");
        if (reason == null || reason.isBlank()) return Result.fail("请输入注销原因");
        userService.logoff(userId, reason, cashPassword);
        return Result.ok();
    }

    /** 图片验证码（对应旧LocalUserController.getImageCode） */
    @GetMapping("/image-code")
    public Result<?> getImageCode() {
        return Result.ok(userService.getImageCode());
    }

    /** 推广分享信息（对应旧LocalUserController.getShare） */
    @GetMapping("/share")
    public Result<?> getShare(@RequestAttribute Long userId) {
        return Result.ok(userService.getShare(userId));
    }

    /** 更新头像（对应旧LocalUserController.refreshAvatar） */
    @PutMapping("/avatar")
    public Result<?> refreshAvatar(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String idxStr = body.get("idx");
        if (idxStr == null) return Result.fail("头像序号不能为空");
        userService.refreshAvatar(userId, Integer.parseInt(idxStr));
        return Result.ok();
    }

    /** 退出登录 — Token加入黑名单即时失效 */
    @PostMapping("/logout")
    public Result<?> logout(HttpServletRequest request) {
        String token = request.getHeader("Authorization");
        if (token != null && token.startsWith("Bearer ")) {
            jwtUtil.revokeToken(token.substring(7));
        }
        return Result.ok();
    }
}
