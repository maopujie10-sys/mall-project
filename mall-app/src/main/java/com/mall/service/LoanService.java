package com.mall.service;

import java.util.Map;

public interface LoanService {
    void apply(Long userId, Map<String, Object> dto);
    Map<String, Object> list(Long userId, Integer page, Integer pageSize);
    Map<String, Object> detail(Long userId, String uuid);
    void repay(Long userId, String uuid, Map<String, Object> dto);
    Map<String, Object> config();
    Map<String, Object> adminList(String keyword, Integer status, Integer page, Integer pageSize);
    void audit(Long adminId, String uuid, Map<String, Object> dto);
    void saveConfig(Map<String, Object> dto);
    Map<String, Object> configList();
}
