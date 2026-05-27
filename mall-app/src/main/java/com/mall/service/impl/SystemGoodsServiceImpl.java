package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.SystemGoods;
import com.mall.mapper.ProductSkuMapper;
import com.mall.mapper.SystemGoodsMapper;
import com.mall.service.SystemGoodsService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class SystemGoodsServiceImpl implements SystemGoodsService {

    private final SystemGoodsMapper systemGoodsMapper;
    private final ProductSkuMapper productSkuMapper;

    @Override
    public Map<String, Object> adminList(String name, String categoryId, Integer isShelf, Integer updateStatus, Integer pageNum, Integer pageSize) {
        int p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<SystemGoods> qw = new QueryWrapper<>();
        if (name != null && !name.isEmpty()) qw.like("goods_name", name);
        if (categoryId != null && !categoryId.isEmpty()) qw.eq("category_id", categoryId);
        if (isShelf != null) qw.eq("status", isShelf);
        qw.orderByDesc("create_time");
        Page<SystemGoods> pg = new Page<>(p, ps);
        Page<SystemGoods> result = systemGoodsMapper.selectPage(pg, qw);
        Map<String, Object> r = new HashMap<>();
        r.put("total", result.getTotal());
        r.put("page", p);
        r.put("pageSize", ps);
        r.put("list", result.getRecords());
        return r;
    }

    @Override
    public Map<String, Object> adminDetail(String id, String lang) {
        SystemGoods goods = systemGoodsMapper.selectById(id);
        if (goods == null) throw new BizException("商品不存在");
        Map<String, Object> dto = new HashMap<>();
        dto.put("uuid", goods.getUuid());
        dto.put("systemPrice", goods.getSystemPrice());
        dto.put("categoryId", goods.getCategoryId());
        dto.put("secondaryCategoryId", goods.getSecondaryCategoryId());
        dto.put("goodsName", goods.getGoodsName());
        dto.put("goodsDesc", goods.getGoodsDesc());
        dto.put("mainImage", goods.getMainImage());
        dto.put("detailImages", goods.getDetailImages());
        dto.put("status", goods.getStatus());
        dto.put("isHot", goods.getIsHot());
        dto.put("isNew", goods.getIsNew());
        dto.put("sort", goods.getSort());
        dto.put("brandName", goods.getBrandName());
        dto.put("createTime", goods.getCreateTime());
        dto.put("updateTime", goods.getUpdateTime());
        return dto;
    }

    @Override
    @Transactional
    public void adminSave(Map<String, Object> dto) {
        SystemGoods g = new SystemGoods();
        g.setUuid(UUID.randomUUID().toString().replace("-", ""));
        g.setSystemPrice((String) dto.getOrDefault("systemPrice", "0"));
        g.setCategoryId((String) dto.get("categoryId"));
        g.setSecondaryCategoryId((String) dto.getOrDefault("secondaryCategoryId", ""));
        g.setGoodsName((String) dto.get("goodsName"));
        g.setGoodsDesc((String) dto.getOrDefault("goodsDesc", ""));
        g.setMainImage((String) dto.getOrDefault("mainImage", ""));
        g.setDetailImages((String) dto.getOrDefault("detailImages", ""));
        g.setStatus((Integer) dto.getOrDefault("status", 0));
        g.setIsHot((Integer) dto.getOrDefault("isHot", 0));
        g.setIsNew((Integer) dto.getOrDefault("isNew", 0));
        g.setSort((Integer) dto.getOrDefault("sort", 0));
        g.setBrandName((String) dto.getOrDefault("brandName", ""));
        g.setCreateTime(LocalDateTime.now());
        g.setUpdateTime(LocalDateTime.now());
        systemGoodsMapper.insert(g);
    }

    @Override
    @Transactional
    public void adminUpdate(Map<String, Object> dto) {
        String id = (String) dto.get("id");
        SystemGoods g = systemGoodsMapper.selectById(id);
        if (g == null) throw new BizException("商品不存在");
        if (dto.containsKey("systemPrice")) g.setSystemPrice((String) dto.get("systemPrice"));
        if (dto.containsKey("categoryId")) g.setCategoryId((String) dto.get("categoryId"));
        if (dto.containsKey("secondaryCategoryId")) g.setSecondaryCategoryId((String) dto.get("secondaryCategoryId"));
        if (dto.containsKey("goodsName")) g.setGoodsName((String) dto.get("goodsName"));
        if (dto.containsKey("goodsDesc")) g.setGoodsDesc((String) dto.get("goodsDesc"));
        if (dto.containsKey("mainImage")) g.setMainImage((String) dto.get("mainImage"));
        if (dto.containsKey("detailImages")) g.setDetailImages((String) dto.get("detailImages"));
        if (dto.containsKey("status")) g.setStatus((Integer) dto.get("status"));
        if (dto.containsKey("isHot")) g.setIsHot((Integer) dto.get("isHot"));
        if (dto.containsKey("isNew")) g.setIsNew((Integer) dto.get("isNew"));
        if (dto.containsKey("sort")) g.setSort((Integer) dto.get("sort"));
        if (dto.containsKey("brandName")) g.setBrandName((String) dto.get("brandName"));
        g.setUpdateTime(LocalDateTime.now());
        systemGoodsMapper.updateById(g);
    }

    @Override
    @Transactional
    public void adminDelete(String id) {
        SystemGoods g = systemGoodsMapper.selectById(id);
        if (g == null) throw new BizException("商品不存在");
        systemGoodsMapper.deleteById(id);
    }

    @Override
    public Map<String, Object> merchantList(String keyword, Integer pageNum, Integer pageSize) {
        int p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<SystemGoods> qw = new QueryWrapper<>();
        qw.eq("status", 1);
        if (keyword != null && !keyword.isEmpty()) qw.like("goods_name", keyword);
        qw.orderByDesc("create_time");
        Page<SystemGoods> pg = new Page<>(p, ps);
        Page<SystemGoods> result = systemGoodsMapper.selectPage(pg, qw);
        List<Map<String, Object>> records = new ArrayList<>();
        for (SystemGoods g : result.getRecords()) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("id", g.getUuid());
            item.put("goodsName", g.getGoodsName());
            item.put("image", g.getMainImage());
            item.put("price", g.getSystemPrice());
            item.put("categoryId", g.getCategoryId());
            item.put("brandName", g.getBrandName());
            records.add(item);
        }
        Map<String, Object> r = new HashMap<>();
        r.put("records", records);
        r.put("total", result.getTotal());
        return r;
    }

    @Override
    @Transactional
    public void adminUpdateShelf(String id, Integer isShelf) {
        SystemGoods g = systemGoodsMapper.selectById(id);
        if (g == null) throw new BizException("商品不存在");
        g.setStatus(isShelf);
        g.setUpdateTime(LocalDateTime.now());
        systemGoodsMapper.updateById(g);
    }

    @Override
    @Transactional
    public void deleteSku(String skuId) {
        productSkuMapper.deleteById(skuId);
    }
}
