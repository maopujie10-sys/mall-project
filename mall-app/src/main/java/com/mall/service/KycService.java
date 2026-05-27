package com.mall.service;

import java.util.List;
import java.util.Map;

public interface KycService {
    void submit(Long userId, Map<String, Object> dto);
    Map<String, Object> status(Long userId);
    List<Map<String, Object>> list(Integer pageNum, Integer pageSize, Integer status);
    void audit(Long id, Boolean approved, String reason, Long adminId);
}
