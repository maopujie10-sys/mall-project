package com.mall.service;

import java.util.List;
import java.util.Map;

public interface SubscribeService {
    void subscribe(Long userId, Map<String, Object> dto);
    List<Map<String, Object>> list(Long userId);
    void update(Long userId, Long id, Map<String, Object> dto);
    void delete(Long userId, Long id);

    // Admin
    Map<String, Object> adminList(String email, String startTime, String endTime, Integer page, Integer pageSize);
    void adminDelete(Long id);
    void adminPush(Map<String, Object> dto);
}
