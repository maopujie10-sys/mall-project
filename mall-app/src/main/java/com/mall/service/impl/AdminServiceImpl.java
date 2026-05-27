package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.JwtUtil;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.AdminService;
import com.mall.service.RechargeService;
import com.mall.service.WithdrawService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class AdminServiceImpl implements AdminService {

    private final AdminMapper adminMapper;
    private final UserMapper userMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final BalanceLogMapper balanceLogMapper;
    private final RechargeOrderMapper rechargeMapper;
    private final WithdrawOrderMapper withdrawMapper;
    private final MallOrderMapper orderMapper;
    private final MerchantApplyMapper merchantApplyMapper;
    private final MerchantMapper merchantMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final ProductMapper productMapper;
    private final MallOrdersGoodsMapper ordersGoodsMapper;
    private final RechargeService rechargeService;
    private final WithdrawService withdrawService;
    private final MallSellerMapper sellerMapper;
    private final MallLevelMapper mallLevelMapper;
    private final MallOrderRebateMapper rebateMapper;
    private final MallClientSellerMapper mallClientSellerMapper;
    private final NotificationMapper notificationMapper;
    private final UserSafewordApplyMapper safewordApplyMapper;

    @Override
    public Map<String, Object> login(String username, String password) {
        Admin admin = adminMapper.selectOne(new QueryWrapper<Admin>().eq("username", username));
        if (admin == null) throw new BizException("管理员不存在");
        if (!passwordEncoder.matches(password, admin.getPassword()))
            throw new BizException("密码错误");
        String token = jwtUtil.generateToken(admin.getId(), "ADMIN");
        admin.setPassword(null);
        return Map.of("token", token, "info", admin);
    }

    @Override
    public Map<String, Object> dashboard() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("todayOrders", orderMapper.countTodayOrders());
        data.put("todayAmount", orderMapper.sumTodayAmount());
        data.put("todayRecharge", rechargeMapper.sumTodayRecharge());
        data.put("todayWithdraw", withdrawMapper.sumTodayWithdraw());
        data.put("pendingRecharge", rechargeMapper.countPending());
        data.put("pendingWithdraw", withdrawMapper.countPending());
        data.put("pendingMerchant", merchantApplyMapper.countPending());
        data.put("totalOrders", orderMapper.countAll());
        data.put("totalUsers", userMapper.selectCount(new QueryWrapper<User>().eq("deleted", 0)));
        data.put("totalMerchants", merchantMapper.selectCount(new QueryWrapper<Merchant>().eq("status", 1)));
        data.put("orderStatusBreakdown", orderMapper.countByStatus());
        data.put("dailyTrend", orderMapper.dailyStats(7));
        data.put("topProducts", ordersGoodsMapper.topProducts(10));
        return data;
    }

    @Override
    public Map<String, Object> userList(String keyword, Integer status, Integer pageNum, Integer pageSize) {
        QueryWrapper<User> w = new QueryWrapper<User>().eq("deleted", 0);
        if (keyword != null && !keyword.isBlank()) w.like("phone", keyword).or().like("nickname", keyword);
        if (status != null) w.eq("status", status);
        w.orderByDesc("create_time");
        IPage<User> page = userMapper.selectPage(new Page<>(pageNum, pageSize), w);
        page.getRecords().forEach(u -> u.setPassword(null));
        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("list", page.getRecords());
        return result;
    }

    @Override
    public void updateUserStatus(Long userId, Integer status) {
        User user = new User();
        user.setId(userId);
        user.setStatus(status);
        userMapper.updateById(user);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void adjustBalance(Long userId, BigDecimal amount, String remark, Long adminId) {
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            UserBalance balance = userBalanceMapper.selectOne(
                new QueryWrapper<UserBalance>().eq("user_id", userId));
            if (balance == null) throw new BizException("用户余额账户不存在");
            BigDecimal afterAdjust = balance.getBalance().add(amount);
            if (afterAdjust.compareTo(balance.getFrozen()) < 0)
                throw new BizException("调整后余额不能低于冻结金额");
        }
        userBalanceMapper.addBalance(userId, amount);
        balanceLogMapper.insert(BalanceLog.builder()
            .userId(userId).amount(amount)
            .type("ADMIN_ADJUST").remark("管理员调整：" + remark)
            .relatedId(adminId).build());
    }

    @Override
    public Map<String, Object> rechargePending(Integer pageNum, Integer pageSize) {
        IPage<RechargeOrder> page = rechargeMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<RechargeOrder>().eq("status", 0).orderByDesc("create_time"));
        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("list", page.getRecords());
        return result;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void auditRecharge(Long id, Boolean approved, String reason, Long adminId) {
        rechargeService.audit(id, approved, reason, adminId);
    }

    @Override
    public Map<String, Object> withdrawPending(Integer pageNum, Integer pageSize) {
        IPage<WithdrawOrder> page = withdrawMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<WithdrawOrder>().eq("status", 0).orderByDesc("create_time"));
        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("list", page.getRecords());
        return result;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void auditWithdraw(Long id, Boolean approved, String txHash, String reason, Long adminId) {
        withdrawService.audit(id, approved, txHash, reason, adminId);
    }

    @Override
    public Map<String, Object> merchantApplyList(Integer pageNum, Integer pageSize) {
        IPage<MerchantApply> page = merchantApplyMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<MerchantApply>().eq("status", 0).orderByDesc("create_time"));
        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("list", page.getRecords());
        return result;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void auditMerchantApply(Long applyId, Boolean approved, String reason, Long adminId) {
        MerchantApply apply = merchantApplyMapper.selectById(applyId);
        if (apply.getStatus() != 0) throw new BizException("该申请已处理");
        if (approved) {
            apply.setStatus(1);
            Merchant merchant = Merchant.builder()
                .userId(apply.getUserId()).shopName(apply.getShopName())
                .shopPhone(apply.getShopPhone()).shopAddress(apply.getShopAddress())
                .contact(apply.getContact()).status(1).build();
            merchantMapper.insert(merchant);
        } else {
            apply.setStatus(2);
            apply.setRejectReason(reason);
        }
        apply.setAuditAdminId(adminId);
        apply.setAuditTime(LocalDateTime.now());
        merchantApplyMapper.updateById(apply);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void forceRefund(Long orderId, Long adminId) {
        MallOrder order = orderMapper.selectById(orderId.toString());
        if (order == null) throw new BizException("订单不存在");
        if (order.getOrderStatus() == 4) throw new BizException("订单已取消");
        order.setOrderStatus(4);
        orderMapper.updateById(order);

        Long userId = Long.valueOf(order.getPartyId());
        userBalanceMapper.addBalance(userId, order.getPayAmount());
        balanceLogMapper.insert(BalanceLog.builder()
            .userId(userId).amount(order.getPayAmount())
            .type("REFUND").remark("管理员强制退款，订单：" + order.getOrderNo())
            .relatedId(orderId).build());
    }

    @Override
    public Map<String, Object> productList(String keyword, Integer status, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<Product> w = new QueryWrapper<>();
        if (keyword != null && !keyword.isBlank()) w.like("name", keyword);
        if (status != null) w.eq("status", status);
        w.orderByDesc("create_time");
        IPage<Product> pg = productMapper.selectPage(new Page<>(p, ps), w);
        Map<String, Object> result = new HashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", p);
        result.put("pageSize", ps);
        result.put("list", pg.getRecords());
        return result;
    }

    @Override
    public void auditProduct(Long productId, Integer status, Long adminId) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        product.setStatus(status);
        productMapper.updateById(product);
    }

    @Override
    public Map<String, Object> merchantList(String keyword, Integer status, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<Merchant> w = new QueryWrapper<>();
        if (keyword != null && !keyword.isBlank())
            w.and(wr -> wr.like("shop_name", keyword).or().like("contact", keyword));
        if (status != null) w.eq("status", status);
        w.orderByDesc("create_time");
        IPage<Merchant> pg = merchantMapper.selectPage(new Page<>(p, ps), w);
        Map<String, Object> result = new HashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", p);
        result.put("pageSize", ps);
        result.put("list", pg.getRecords());
        return result;
    }

    @Override
    public void updateMerchantStatus(Long merchantId, Integer status) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");
        merchant.setStatus(status);
        merchantMapper.updateById(merchant);
    }

    @Override
    public Map<String, Object> orderList(String keyword, Integer status, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallOrder> w = new QueryWrapper<>();
        if (keyword != null && !keyword.isBlank())
            w.and(wr -> wr.like("order_no", keyword).or().like("party_id", keyword));
        if (status != null) w.eq("order_status", status);
        w.orderByDesc("create_time");
        IPage<MallOrder> pg = orderMapper.selectPage(new Page<>(p, ps), w);
        Map<String, Object> result = new HashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", p);
        result.put("pageSize", ps);
        result.put("list", pg.getRecords());
        return result;
    }

    // === 商品管理增强 ===

    @Override
    public Map<String, Object> productDetail(Long productId) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("product", product);
        return result;
    }

    @Override
    public void productUpdate(Long productId, Product product) {
        Product existing = productMapper.selectById(productId);
        if (existing == null) throw new BizException("商品不存在");
        product.setId(productId);
        productMapper.updateById(product);
    }

    @Override
    public void productDelete(Long productId) {
        Product existing = productMapper.selectById(productId);
        if (existing == null) throw new BizException("商品不存在");
        productMapper.deleteById(productId);
    }

    // ======================== 代理管理 ========================

    @Override
    public Map<String, Object> agentList(String keyword, String level, Integer status, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallSeller> w = new QueryWrapper<>();
        if (keyword != null && !keyword.isBlank())
            w.and(wr -> wr.like("NAME", keyword).or().like("CONTACT", keyword));
        if (level != null && !level.isBlank()) w.eq("MALL_LEVEL", level);
        if (status != null) w.eq("STATUS", status);
        w.orderByDesc("CREATE_TIME");
        IPage<MallSeller> pg = sellerMapper.selectPage(new Page<>(p, ps), w);
        Map<String, Object> result = new HashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", p);
        result.put("pageSize", ps);
        result.put("list", pg.getRecords());
        return result;
    }

    @Override
    public Map<String, Object> agentDetail(String sellerId) {
        MallSeller seller = sellerMapper.selectById(sellerId);
        if (seller == null) throw new BizException("代理不存在");
        Map<String, Object> detail = new LinkedHashMap<>();
        detail.put("info", seller);
        detail.put("teamCount", seller.getTeamNum() != null ? seller.getTeamNum() : 0);
        detail.put("childCount", seller.getChildNum() != null ? seller.getChildNum() : 0);
        detail.put("inviteCount", seller.getInviteNum() != null ? seller.getInviteNum() : 0);
        // 累计佣金（列名 party_id，非 PARTY_ID）
        Double totalRebate = rebateMapper.selectList(
            new QueryWrapper<MallOrderRebate>().eq("party_id", sellerId))
            .stream().mapToDouble(r -> r.getRebateAmount() != null ? r.getRebateAmount() : 0).sum();
        detail.put("totalRebate", totalRebate);
        return detail;
    }

    @Override
    public void updateAgentStatus(String sellerId, Integer status) {
        MallSeller seller = sellerMapper.selectById(sellerId);
        if (seller == null) throw new BizException("代理不存在");
        seller.setStatus(status);
        sellerMapper.updateById(seller);
    }

    @Override
    public Map<String, Object> agentTeam(String sellerId, Integer page, Integer pageSize) {
        // V5 mall_seller 无 parent_id 层级关系字段，teamNum/childNum 为预计算统计值
        // agentDetail 已返回 teamCount/childCount，此处返回空列表待后续扩展
        Map<String, Object> result = new HashMap<>();
        result.put("total", 0);
        result.put("page", page != null ? page : 1);
        result.put("pageSize", pageSize != null ? pageSize : 20);
        result.put("list", Collections.emptyList());
        return result;
    }

    @Override
    public List<Map<String, Object>> agentLevelList() {
        List<MallLevel> levels = mallLevelMapper.selectList(
            new QueryWrapper<MallLevel>().orderByAsc("LEVEL"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallLevel lv : levels) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("uuid", lv.getUuid());
            m.put("level", lv.getLevel());
            m.put("title", lv.getTitle());
            m.put("profitRationMin", lv.getProfitRationMin());
            m.put("profitRationMax", lv.getProfitRationMax());
            m.put("teamNum", lv.getTeamNum());
            m.put("upgradeCash", lv.getUpgradeCash());
            m.put("sellerDiscount", lv.getSellerDiscount());
            m.put("condExpr", lv.getCondExpr());
            m.put("createTime", lv.getCreateTime());
            list.add(m);
        }
        return list;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void agentLevelSave(Map<String, Object> data) {
        String uuid = (String) data.get("uuid");
        MallLevel level;
        if (uuid != null && !uuid.isBlank()) {
            level = mallLevelMapper.selectById(uuid);
            if (level == null) throw new BizException("等级不存在");
        } else {
            level = new MallLevel();
        }
        if (data.containsKey("level")) level.setLevel((String) data.get("level"));
        if (data.containsKey("title")) level.setTitle((String) data.get("title"));
        if (data.containsKey("profitRationMin")) level.setProfitRationMin(Double.valueOf(data.get("profitRationMin").toString()));
        if (data.containsKey("profitRationMax")) level.setProfitRationMax(Double.valueOf(data.get("profitRationMax").toString()));
        if (data.containsKey("teamNum")) level.setTeamNum(Integer.valueOf(data.get("teamNum").toString()));
        if (data.containsKey("upgradeCash")) level.setUpgradeCash(Integer.valueOf(data.get("upgradeCash").toString()));
        if (data.containsKey("sellerDiscount")) level.setSellerDiscount(Double.valueOf(data.get("sellerDiscount").toString()));
        if (data.containsKey("condExpr")) level.setCondExpr((String) data.get("condExpr"));
        if (uuid == null || uuid.isBlank()) {
            level.setUuid(java.util.UUID.randomUUID().toString().replace("-", ""));
            mallLevelMapper.insert(level);
        } else {
            mallLevelMapper.updateById(level);
        }
    }

    @Override
    public void agentLevelDelete(String uuid) {
        mallLevelMapper.deleteById(uuid);
    }

    @Override
    public Map<String, Object> agentRebateList(String keyword, String level, String startDate, String endDate,
                                                Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallOrderRebate> w = new QueryWrapper<>();
        if (keyword != null && !keyword.isBlank())
            w.and(wr -> wr.like("ORDER_ID", keyword).or().like("PARTY_ID", keyword));
        if (level != null && !level.isBlank()) w.eq("LEVEL", level);
        if (startDate != null && !startDate.isBlank()) w.ge("CREATE_TIME", startDate);
        if (endDate != null && !endDate.isBlank()) w.le("CREATE_TIME", endDate + " 23:59:59");
        w.orderByDesc("CREATE_TIME");
        IPage<MallOrderRebate> pg = rebateMapper.selectPage(new Page<>(p, ps), w);
        Map<String, Object> result = new HashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", p);
        result.put("pageSize", ps);
        result.put("list", pg.getRecords());
        return result;
    }

    @Override
    public Map<String, Object> agentRebateStats() {
        List<MallOrderRebate> all = rebateMapper.selectList(null);
        double total = all.stream().mapToDouble(r -> r.getRebateAmount() != null ? r.getRebateAmount() : 0).sum();
        long count = all.size();
        // 按等级统计
        Map<String, Double> byLevel = new LinkedHashMap<>();
        Map<String, Integer> countByLevel = new LinkedHashMap<>();
        for (MallOrderRebate r : all) {
            String lv = r.getLevel() != null ? String.valueOf(r.getLevel()) : "未知";
            byLevel.merge(lv, r.getRebateAmount() != null ? r.getRebateAmount() : 0, Double::sum);
            countByLevel.merge(lv, 1, Integer::sum);
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("totalRebate", total);
        result.put("totalCount", count);
        result.put("byLevel", byLevel);
        result.put("countByLevel", countByLevel);
        return result;
    }

    // === 商品管理增强 ===

    @Override
    public void productCreate(Product product) {
        product.setCreateTime(java.time.LocalDateTime.now());
        productMapper.insert(product);
    }

    @Override
    public void productUpdateStatus(Long productId, Integer status) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        product.setStatus(status);
        productMapper.updateById(product);
    }

    // === 订单管理增强 ===

    @Override
    public Map<String, Object> orderDetail(Long orderId) {
        MallOrder order = orderMapper.selectById(orderId.toString());
        if (order == null) throw new BizException("订单不存在");
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("order", order);
        // 查订单商品
        List<MallOrdersGoods> goods = ordersGoodsMapper.selectList(
            new QueryWrapper<MallOrdersGoods>().eq("ORDER_ID", orderId));
        result.put("goods", goods);
        return result;
    }

    @Override
    public void updateOrderStatus(Long orderId, Integer status) {
        MallOrder order = orderMapper.selectById(orderId.toString());
        if (order == null) throw new BizException("订单不存在");
        order.setOrderStatus(status);
        order.setUpdateTime(java.time.LocalDateTime.now());
        orderMapper.updateById(order);
    }

    // === 通知管理 ===

    @Override
    public Map<String, Object> notificationList(Integer pageNum, Integer pageSize, String type, String keyword) {
        QueryWrapper<Notification> qw = new QueryWrapper<>();
        if (type != null && !type.isBlank()) qw.eq("type", type);
        if (keyword != null && !keyword.isBlank())
            qw.and(w -> w.like("title", keyword).or().like("content", keyword));
        qw.orderByDesc("create_time");
        IPage<Notification> pg = notificationMapper.selectPage(new Page<>(pageNum, pageSize), qw);
        Map<String, Object> result = new HashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", pageNum);
        result.put("pageSize", pageSize);
        result.put("list", pg.getRecords());
        return result;
    }

    @Override
    public void notificationUpdate(Long id, Notification notification) {
        Notification existing = notificationMapper.selectById(id);
        if (existing == null) throw new BizException("通知不存在");
        notification.setId(id);
        notificationMapper.updateById(notification);
    }

    @Override
    public void notificationAdminDelete(Long id) {
        notificationMapper.deleteById(id);
    }

    // === 安全重置审核（窗口3） ===

    @Override
    public Map<String, Object> safewordApplyList(Integer page, Integer pageSize, String keyword, Integer status, Integer operate) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<UserSafewordApply> w = new QueryWrapper<>();
        if (status != null) w.eq("status", status);
        if (operate != null) w.eq("operate", operate);
        w.orderByDesc("create_time");
        IPage<UserSafewordApply> pg = safewordApplyMapper.selectPage(new Page<>(p, ps), w);
        Map<String, Object> result = new HashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", p);
        result.put("pageSize", ps);
        result.put("list", pg.getRecords());
        return result;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void safewordApprove(Long id, Long adminId, String adminSafeword) {
        // 验证管理员资金密码
        Admin admin = adminMapper.selectById(adminId);
        if (admin == null) throw new BizException("管理员不存在");
        if (admin.getSafeword() == null || admin.getSafeword().isEmpty())
            throw new BizException("管理员未设置资金密码");
        if (!passwordEncoder.matches(adminSafeword, admin.getSafeword()))
            throw new BizException("管理员资金密码错误");

        UserSafewordApply apply = safewordApplyMapper.selectById(id);
        if (apply == null) throw new BizException("申请不存在");
        if (apply.getStatus() != 1) throw new BizException("该申请已处理");

        User user = userMapper.selectById(apply.getUserId());
        if (user == null) throw new BizException("用户不存在");

        switch (apply.getOperate()) {
            case 0:
                user.setSafeword(apply.getSafeword());
                break;
            case 1:
                user.setGoogleAuthSecret(null);
                break;
            case 2:
                user.setPhone(null);
                break;
            case 3:
                user.setEmail(null);
                break;
            default:
                throw new BizException("操作类型不正确");
        }
        userMapper.updateById(user);

        apply.setStatus(2);
        apply.setAuditAdminId(adminId);
        apply.setApplyTime(LocalDateTime.now());
        safewordApplyMapper.updateById(apply);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void safewordReject(Long id, Long adminId, String msg) {
        UserSafewordApply apply = safewordApplyMapper.selectById(id);
        if (apply == null) throw new BizException("申请不存在");
        if (apply.getStatus() != 1) throw new BizException("该申请已处理");

        apply.setStatus(3);
        apply.setMsg(msg);
        apply.setAuditAdminId(adminId);
        apply.setApplyTime(LocalDateTime.now());
        safewordApplyMapper.updateById(apply);
    }
}
