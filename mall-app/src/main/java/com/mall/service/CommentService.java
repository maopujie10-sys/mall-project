package com.mall.service;

import java.util.Map;

public interface CommentService {
    Map<String, Object> listByGoodId(String goodId, Integer page, Integer pageSize);
    void add(Long userId, Map<String, Object> dto);
    void delete(Long userId, String uuid);
}
