package com.mall.service;

import com.mall.common.PageResult;
import java.util.Map;

public interface ProductService {
    PageResult<Map<String, Object>> getList(Long categoryId, String keyword, Integer pageNum, Integer pageSize);
    Map<String, Object> getDetail(Long productId);
    Long save(Map<String, Object> dto);
}
