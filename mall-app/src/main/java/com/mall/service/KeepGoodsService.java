package com.mall.service;

import java.util.List;
import java.util.Map;

public interface KeepGoodsService {
    void add(Long userId, String sellerGoodsId);
    void remove(Long userId, String sellerGoodsId);
    List<Map<String, Object>> list(Long userId, int page, int pageSize);
    boolean isKept(Long userId, String sellerGoodsId);
    long count(Long userId);
}
