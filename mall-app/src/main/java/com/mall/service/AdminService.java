package com.mall.service;

import com.mall.entity.Notification;
import com.mall.entity.Product;
import java.math.BigDecimal;
import java.util.Map;
import java.util.List;

public interface AdminService {
    Map<String, Object> login(String username, String password);
    Map<String, Object> dashboard();
    Map<String, Object> userList(String keyword, Integer status, Integer pageNum, Integer pageSize);
    void updateUserStatus(Long userId, Integer status);
    void adjustBalance(Long userId, BigDecimal amount, String remark, Long adminId);
    Map<String, Object> rechargePending(Integer pageNum, Integer pageSize);
    void auditRecharge(Long id, Boolean approved, String reason, Long adminId);
    Map<String, Object> withdrawPending(Integer pageNum, Integer pageSize);
    void auditWithdraw(Long id, Boolean approved, String txHash, String reason, Long adminId);
    Map<String, Object> merchantApplyList(Integer pageNum, Integer pageSize);
    void auditMerchantApply(Long applyId, Boolean approved, String reason, Long adminId);
    void forceRefund(Long orderId, Long adminId);
    Map<String, Object> productList(String keyword, Integer status, Integer page, Integer pageSize);
    void auditProduct(Long productId, Integer status, Long adminId);
    Map<String, Object> productDetail(Long productId);
    void productUpdate(Long productId, Product product);
    void productDelete(Long productId);
    Map<String, Object> merchantList(String keyword, Integer status, Integer page, Integer pageSize);
    void updateMerchantStatus(Long merchantId, Integer status);
    Map<String, Object> orderList(String keyword, Integer status, Integer page, Integer pageSize);

    // === 代理管理 ===
    Map<String, Object> agentList(String keyword, String level, Integer status, Integer page, Integer pageSize);
    Map<String, Object> agentDetail(String sellerId);
    void updateAgentStatus(String sellerId, Integer status);
    Map<String, Object> agentTeam(String sellerId, Integer page, Integer pageSize);
    List<Map<String, Object>> agentLevelList();
    void agentLevelSave(Map<String, Object> data);
    void agentLevelDelete(String uuid);
    Map<String, Object> agentRebateList(String keyword, String level, String startDate, String endDate, Integer page, Integer pageSize);
    Map<String, Object> agentRebateStats();

    // === 商品管理增强 ===
    void productCreate(Product product);
    void productUpdateStatus(Long productId, Integer status);

    // === 订单管理增强 ===
    Map<String, Object> orderDetail(Long orderId);
    void updateOrderStatus(Long orderId, Integer status);

    // === 通知管理 ===
    Map<String, Object> notificationList(Integer pageNum, Integer pageSize, String type, String keyword);
    void notificationUpdate(Long id, Notification notification);
    void notificationAdminDelete(Long id);

    // === 安全重置审核（窗口3） ===
    Map<String, Object> safewordApplyList(Integer page, Integer pageSize, String keyword, Integer status, Integer operate);
    void safewordApprove(Long id, Long adminId, String adminSafeword);
    void safewordReject(Long id, Long adminId, String msg);
}
