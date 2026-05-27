package com.mall.service;

import java.util.Map;

public interface MerchantService {
    // Auth
    Map<String, Object> loginByUsername(String username, String password);
    void changePassword(Long merchantId, String oldPassword, String newPassword);
    void resetPasswordSendCode(String phone, String ip);
    void resetPassword(String phone, String code, String newPassword);

    // Dashboard
    Map<String, Object> dashboard(Long merchantId);

    // Info & Store
    Object getInfo(Long merchantId);
    void updateShopInfo(Long merchantId, Map<String, Object> data);

    // Product CRUD
    Map<String, Object> productList(Long merchantId, Integer pageNum, Integer pageSize, String keyword, Integer status);
    Map<String, Object> productDetail(Long merchantId, Long productId);
    void productAdd(Long merchantId, Map<String, Object> data);
    void productUpdate(Long merchantId, Long productId, Map<String, Object> data);
    void productDelete(Long merchantId, Long productId);
    void productUpdateStatus(Long merchantId, Long productId, Integer status);

    // Orders
    Map<String, Object> orderList(Long merchantId, Integer pageNum, Integer pageSize, Integer status);
    Map<String, Object> orderDetail(Long merchantId, String orderId);
    void shipOrder(Long merchantId, String orderId, String company, String trackingNo);

    // Reviews
    Map<String, Object> reviewList(Long merchantId, Integer pageNum, Integer pageSize);

    // Refund
    Map<String, Object> refundList(Long merchantId, Integer pageNum, Integer pageSize);
    void refundProcess(Long merchantId, String orderId, Boolean approved);

    // Wallet
    Map<String, Object> walletInfo(Long merchantId);
    Map<String, Object> rechargeList(Long merchantId, Integer pageNum, Integer pageSize);
    Map<String, Object> withdrawList(Long merchantId, Integer pageNum, Integer pageSize);
    void rechargeApply(Long merchantId, Map<String, Object> data);
    void withdrawApply(Long merchantId, Map<String, Object> data);

    // Balance log
    Map<String, Object> balanceLogList(Long merchantId, Integer pageNum, Integer pageSize);

    // Financial report
    Map<String, Object> financeReport(Long merchantId, String startDate, String endDate);

    // Customer service
    Map<String, Object> chatList(Long merchantId, Integer pageNum, Integer pageSize);
    Map<String, Object> chatConversation(Long merchantId, Long fromUserId);
    void chatReply(Long merchantId, Long toUserId, String content);

    // Settle (merchant apply)
    void settle(Map<String, Object> data);
    Map<String, Object> settleStatus(String phone);

    // Account
    void deleteAccount(Long merchantId, String password, String reason);

    // Library
    Map<String, Object> libraryList(String keyword, Integer pageNum, Integer pageSize);
    void libraryPurchase(Long merchantId, String systemGoodsId);

    // Car / Promote
    void carBuy(Long merchantId, Integer days);
    java.util.List<Map<String, Object>> carHistory(Long merchantId);

    // SKU management
    java.util.List<com.mall.entity.ProductSku> skuList(Long merchantId, String productId);
    void skuAdd(Long merchantId, String productId, Map<String, Object> data);
    void skuUpdate(Long merchantId, String skuId, Map<String, Object> data);
    void skuDelete(Long merchantId, String skuId);
}
