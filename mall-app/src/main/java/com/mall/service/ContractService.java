package com.mall.service;

import java.util.Map;

public interface ContractService {
    Map<String, Object> contractInfo();
    void signContract(Long userId, String contractType, String contractContent);
    java.util.List<Map<String, Object>> myContracts(Long userId);
}
