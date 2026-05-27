package com.mall.service;

import java.math.BigDecimal;
import java.util.Map;
import java.util.List;

public interface WithdrawService {
    Map<String, Object> apply(Long userId, BigDecimal amount, String usdtAddress);
    List<Map<String, Object>> list(Long userId, Integer pageNum, Integer pageSize);
    Map<String, Object> getFee(Long userId, String channel);
    void audit(Long id, Boolean approved, String txHash, String reason, Long adminId);
}
