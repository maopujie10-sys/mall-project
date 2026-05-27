package com.mall.service;

import java.util.Map;

public interface PromoteService {
    Map<String, Object> myPromotion(Long userId);
    Map<String, Object> teamInfo(Long userId);
    Map<String, Object> carView(Long userId);
    void carBuy(Long userId, String comboId);
    java.util.List<Map<String, Object>> carHistory(Long userId);
    Map<String, Object> receiveBonus(Long userId);
    Map<String, Object> receiveInviteRewards(Long userId);
}
