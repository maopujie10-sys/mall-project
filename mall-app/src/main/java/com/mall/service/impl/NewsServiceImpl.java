package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.entity.News;
import com.mall.mapper.NewsMapper;
import com.mall.service.NewsService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class NewsServiceImpl implements NewsService {

    private final NewsMapper newsMapper;

    @Override
    public Map<String, Object> list(Integer pageNum, Integer pageSize, String lang) {
        QueryWrapper<News> qw = new QueryWrapper<News>()
            .eq("status", 1)
            .orderByDesc("sort", "create_time");
        if (lang != null && !lang.isBlank()) {
            qw.eq("lang", lang);
        }
        IPage<News> page = newsMapper.selectPage(new Page<>(pageNum, pageSize), qw);

        List<Map<String, Object>> records = page.getRecords().stream()
            .map(this::toMap)
            .collect(Collectors.toList());

        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("page", pageNum);
        result.put("pageSize", pageSize);
        result.put("list", records);
        return result;
    }

    @Override
    public Map<String, Object> getByLang(String lang) {
        QueryWrapper<News> qw = new QueryWrapper<News>()
            .eq("status", 1)
            .orderByDesc("sort", "create_time");
        if (lang != null && !lang.isBlank()) {
            qw.eq("lang", lang);
        }
        qw.last("LIMIT 1");
        News ns = newsMapper.selectOne(qw);
        if (ns == null) {
            return null;
        }
        return toMap(ns);
    }

    @Override
    public Map<String, Object> detail(Long id) {
        News ns = newsMapper.selectById(id);
        if (ns == null) {
            return null;
        }
        return toMap(ns);
    }

    private Map<String, Object> toMap(News ns) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", ns.getId());
        map.put("title", ns.getTitle());
        map.put("content", ns.getContent());
        map.put("lang", ns.getLang());
        map.put("iconImg", ns.getIconImg());
        map.put("releaseTime", ns.getReleaseTime());
        map.put("sort", ns.getSort());
        map.put("createTime", ns.getCreateTime());
        return map;
    }
}
