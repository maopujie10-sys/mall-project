package com.mall.service;

import java.util.List;
import java.util.Map;

public interface WalletService {
    Map<String, Object> logs(Long userId, Integer page, Integer pageSize);
    Map<String, Object> balanceDetail(Long userId);
}
