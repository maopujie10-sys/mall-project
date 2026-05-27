package com.mall.service;

import java.util.Map;
import java.util.List;

public interface OrderService {
    Map<String, Object> createOrder(Long userId, List<Map<String, Object>> items);
    List<Map<String, Object>> list(Long userId, Integer pageNum, Integer pageSize);
    Map<String, Object> detail(Long userId, Long orderId);
    void cancel(Long userId, Long orderId);
    void receipt(Long userId, String orderId);
    Map<String, Integer> countStatus(Long userId);
    void refund(Long userId, Long orderId, String reason);
    void refundApply(Long userId, String orderId, String returnReason, java.math.BigDecimal money, String returnDetail);
    List<Map<String, Object>> listAll(Integer pageNum, Integer pageSize);
    List<Map<String, Object>> saveGoodsBuy(Long userId, String goodsUuid, int num);
}
