package com.mall.service;

import java.util.List;
import java.util.Map;

public interface NewsService {
    Map<String, Object> list(Integer pageNum, Integer pageSize, String lang);
    Map<String, Object> detail(Long id);
    Map<String, Object> getByLang(String lang);
}
