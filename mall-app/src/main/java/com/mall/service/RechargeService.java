package com.mall.service;

import java.math.BigDecimal;
import java.util.Map;
import java.util.List;

public interface RechargeService {
    Map<String, Object> apply(Long userId, BigDecimal amount, String usdtAddress, String txHash, String screenshot);
    List<Map<String, Object>> list(Long userId, Integer pageNum, Integer pageSize);
    void audit(Long id, Boolean approved, String reason, Long adminId);
}
