package com.mall.service;

import java.util.Map;

public interface KycHighLevelService {
    Map<String, Object> get(Long userId);
    void apply(Long userId, Map<String, Object> dto);
    String checkApplyResult(Long userId);
}
