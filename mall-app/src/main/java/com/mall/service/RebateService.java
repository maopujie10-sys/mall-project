package com.mall.service;

import java.util.Map;

public interface RebateService {
    Map<String, Object> list(Long userId, Integer page, Integer pageSize);
    Map<String, Object> detail(Long userId, String uuid);
    Map<String, Object> stats(Long userId);
}
