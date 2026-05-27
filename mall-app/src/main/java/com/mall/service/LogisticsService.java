package com.mall.service;

import java.util.Map;

public interface LogisticsService {
    Map<String, Object> info(Long userId, String orderId);
    Map<String, Object> trace(Long userId, String orderId);
}
