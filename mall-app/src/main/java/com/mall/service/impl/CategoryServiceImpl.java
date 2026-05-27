package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.entity.Category;
import com.mall.mapper.CategoryMapper;
import com.mall.service.CategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class CategoryServiceImpl implements CategoryService {

    private final CategoryMapper categoryMapper;

    @Override
    public List<Map<String, Object>> getTree() {
        List<Category> all = categoryMapper.selectActiveCategories();
        return buildTree(all, null);
    }

    private List<Map<String, Object>> buildTree(List<Category> all, String parentId) {
        List<Map<String, Object>> result = new ArrayList<>();
        for (Category c : all) {
            String pid = c.getParentId();
            if ((parentId == null && pid == null) || (parentId != null && parentId.equals(pid))) {
                Map<String, Object> node = new HashMap<>();
                node.put("id", c.getUuid());
                node.put("name", c.getName());
                node.put("sort", c.getSort());
                node.put("icon", c.getIconImg());
                node.put("level", c.getLevel());
                node.put("type", c.getType());
                node.put("children", buildTree(all, c.getUuid()));
                result.add(node);
            }
        }
        return result;
    }

    @Override
    public Map<String, Object> list(String parentId, Integer level, String startTime, String endTime, Integer page, Integer pageSize) {
        LambdaQueryWrapper<Category> qw = new LambdaQueryWrapper<>();
        if (StringUtils.hasText(parentId)) {
            qw.eq(Category::getParentId, parentId);
        }
        if (level != null && level > 0) {
            qw.eq(Category::getLevel, level);
        }
        if (StringUtils.hasText(startTime)) {
            qw.ge(Category::getCreateTime, startTime.replace(" ", "T"));
        }
        if (StringUtils.hasText(endTime)) {
            qw.le(Category::getCreateTime, endTime.replace(" ", "T"));
        }
        qw.orderByAsc(Category::getSort);
        IPage<Category> result = categoryMapper.selectPage(new Page<>(page, pageSize), qw);
        Map<String, Object> map = new HashMap<>();
        map.put("records", result.getRecords());
        map.put("total", result.getTotal());
        map.put("page", result.getCurrent());
        map.put("pageSize", result.getSize());
        return map;
    }

    @Override
    public Category getById(String uuid) {
        return categoryMapper.selectById(uuid);
    }

    @Override
    public void save(Category category) {
        if (category.getCreateTime() == null) {
            category.setCreateTime(LocalDateTime.now());
        }
        if (category.getStatus() == null) {
            category.setStatus(1);
        }
        if (category.getSort() == null) {
            category.setSort(0);
        }
        if (category.getRank() == null) {
            category.setRank(0);
        }
        if (!StringUtils.hasText(category.getParentId())) {
            category.setParentId("0");
            category.setLevel(1);
        } else {
            category.setLevel("0".equals(category.getParentId()) ? 1 : 2);
        }
        categoryMapper.insert(category);
    }

    @Override
    public void update(Category category) {
        Category existing = categoryMapper.selectById(category.getUuid());
        if (existing == null) {
            throw new RuntimeException("分类不存在");
        }
        if (StringUtils.hasText(category.getParentId())) {
            category.setLevel("0".equals(category.getParentId()) ? 1 : 2);
        }
        category.setCreateTime(existing.getCreateTime());
        categoryMapper.updateById(category);
    }

    @Override
    public void updateStatus(String uuid, Integer status) {
        Category category = categoryMapper.selectById(uuid);
        if (category == null) {
            throw new RuntimeException("分类不存在");
        }
        category.setStatus(status);
        categoryMapper.updateById(category);
    }

    @Override
    public void delete(String uuid) {
        categoryMapper.deleteById(uuid);
    }

    @Override
    public List<Category> listAll() {
        return categoryMapper.selectAllCategories();
    }
}
