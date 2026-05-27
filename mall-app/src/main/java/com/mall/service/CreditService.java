package com.mall.service;

import java.util.List;
import java.util.Map;

public interface CreditService {
    void apply(Long userId, Map<String, Object> dto);
    List<Map<String, Object>> list(Long userId);
    Map<String, Object> detail(Long userId, String uuid);
    void repay(Long userId, String uuid, Map<String, Object> dto);

    // === Admin ===
    Map<String, Object> adminCreditList(String userCode, String userName, String identification,
                                         Integer status, String startTime, String endTime, Integer page, Integer pageSize);
    void adminCreditPass(String creditId, String safeword, String operator);
    void adminCreditOperate(String creditId, String operateType, String rejectReason,
                             String manualRepay, String safeword, String operator);
}
