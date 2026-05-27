package com.mall.service;

import java.util.Map;

public interface LotteryService {
    Map<String, Object> getCurrentActivity(String lang);
    Map<String, Object> getActivityDetail(String activityId, Long userId, String lang);
    int getPoints(String activityId, Long userId);
    Map<String, Object> getCountPoints(String activityId, Long userId);
    Map<String, Object> draw(String activityId, Long userId, int drawTimes, String lang);
    Map<String, Object> countPrize(String activityId, Long userId);
    Map<String, Object> receivePrize(String activityId, Long userId, int prizeType);
    Map<String, Object> pageMyPrizes(String activityId, Long userId, int page, int size);
    java.util.List<Map<String, Object>> listActivityPrize(String activityId);
    void onRechargeApproved(Long userId, java.math.BigDecimal amount);

    // Admin
    Map<String, Object> adminActivityList(String keyword, Integer status, Integer page, Integer pageSize);
    Map<String, Object> adminActivityDetail(String id);
    void adminActivitySave(Map<String, Object> dto);
    void adminActivityUpdate(Map<String, Object> dto);
    void adminActivityToggleShow(String id, Integer isShow);
    void adminActivityDelete(String id);
    java.util.List<Map<String, Object>> adminPrizeListByActivity(String activityId);
    void adminPrizeSave(Map<String, Object> dto);
    void adminPrizeUpdate(Map<String, Object> dto);
    void adminPrizeDelete(String prizeId);
    Map<String, Object> adminRecordList(String username, Integer prizeType, String startTime, String endTime, Integer page, Integer pageSize);
}
