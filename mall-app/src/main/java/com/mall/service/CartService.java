package com.mall.service;

import java.util.Map;
import java.util.List;

public interface CartService {
    void add(Long userId, Long productId, Long skuId, Integer quantity);
    List<Map<String, Object>> list(Long userId);
    void update(Long userId, Long cartId, Integer quantity);
    void remove(Long userId, Long cartId);
}
