package com.mall.service;

import com.mall.entity.Category;
import java.util.List;
import java.util.Map;

public interface CategoryService {
    List<Map<String, Object>> getTree();
    Map<String, Object> list(String parentId, Integer level, String startTime, String endTime, Integer page, Integer pageSize);
    Category getById(String uuid);
    void save(Category category);
    void update(Category category);
    void updateStatus(String uuid, Integer status);
    void delete(String uuid);
    List<Category> listAll();
}
