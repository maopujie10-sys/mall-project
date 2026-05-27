package com.mall.service;

import java.util.List;
import java.util.Map;

public interface FocusSellerService {
    void follow(Long userId, String sellerId);
    void unfollow(Long userId, String sellerId);
    List<Map<String, Object>> list(Long userId, int page, int pageSize);
    boolean isFollowed(Long userId, String sellerId);
    long count(Long userId);
}
