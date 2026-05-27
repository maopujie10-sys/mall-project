package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.PageResult;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.util.*;

@Service
@RequiredArgsConstructor
public class ProductServiceImpl implements ProductService {

    private final ProductMapper productMapper;
    private final ProductWholesaleMapper wholesaleMapper;
    private final ProductSkuMapper skuMapper;
    private final ProductImageMapper productImageMapper;
    private final ProductReviewMapper reviewMapper;

    @Override
    public PageResult<Map<String, Object>> getList(Long categoryId, String keyword, Integer pageNum, Integer pageSize) {
        QueryWrapper<Product> w = new QueryWrapper<>();
        w.eq("status", 1).eq("deleted", 0);
        if (categoryId != null) w.eq("category_id", categoryId);
        if (keyword != null && !keyword.isBlank()) w.like("name", keyword);
        w.orderByDesc("sort", "create_time");

        IPage<Product> page = productMapper.selectPage(new Page<>(pageNum, pageSize), w);

        List<Map<String, Object>> list = new ArrayList<>();
        for (Product p : page.getRecords()) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", p.getId());
            item.put("name", p.getName());
            item.put("mainImage", p.getMainImage());
            item.put("price", p.getPrice());
            item.put("originalPrice", p.getOriginalPrice());
            item.put("sales", p.getSales() + (p.getVirtualSales() != null ? p.getVirtualSales() : 0));
            item.put("isHot", p.getIsHot());
            item.put("isNew", p.getIsNew());
            list.add(item);
        }
        PageResult<Map<String, Object>> result = new PageResult<>();
        result.setTotal(page.getTotal());
        result.setList(list);
        result.setPageNum((int) page.getCurrent());
        result.setPageSize((int) page.getSize());
        return result;
    }

    @Override
    public Map<String, Object> getDetail(Long productId) {
        Product product = productMapper.selectById(productId);
        if (product == null || product.getStatus() == 0) throw new BizException("商品不存在");

        productMapper.addVirtualViews(productId, 1);

        Map<String, Object> detail = new HashMap<>();
        detail.put("id", product.getId());
        detail.put("name", product.getName());
        detail.put("description", product.getDescription());
        detail.put("mainImage", product.getMainImage());
        detail.put("detailImages", product.getDetailImages());
        detail.put("price", product.getPrice());
        detail.put("originalPrice", product.getOriginalPrice());
        detail.put("totalStock", product.getTotalStock());
        detail.put("sales", product.getSales());
        detail.put("virtualSales", product.getVirtualSales());
        detail.put("isWholesale", product.getIsWholesale());

        List<ProductWholesale> wholesalePrices = wholesaleMapper.selectList(
            new QueryWrapper<ProductWholesale>().eq("product_id", productId).orderByAsc("min_quantity"));
        detail.put("wholesalePrices", wholesalePrices);

        List<ProductSku> skuList = skuMapper.selectList(
            new QueryWrapper<ProductSku>().eq("good_id", productId));
        detail.put("skuList", skuList);

        List<ProductImage> images = productImageMapper.selectList(
            new QueryWrapper<ProductImage>().eq("product_id", productId).orderByAsc("sort"));
        detail.put("images", images);

        return detail;
    }

    @Override
    @Transactional
    public Long save(Map<String, Object> dto) {
        Product product = new Product();
        product.setCategoryId(toLong(dto.get("categoryId")));
        product.setBrandId(toLong(dto.get("brandId")));
        product.setName((String) dto.getOrDefault("productName", dto.get("name")));
        product.setSubtitle((String) dto.get("subtitle"));
        product.setDescription((String) dto.getOrDefault("productDesc", dto.get("description")));
        product.setMainImage((String) dto.get("mainImage"));
        product.setDetailImages((String) dto.get("detailImages"));
        product.setPrice(toBigDecimal(dto.get("price")));
        product.setOriginalPrice(toBigDecimal(dto.get("originalPrice")));
        product.setCostPrice(toBigDecimal(dto.get("costPrice")));
        product.setTotalStock(toInt(dto.get("stock"), 0));
        product.setSales(0);
        product.setVirtualSales(toInt(dto.get("virtualSales"), 0));
        product.setVirtualViews(toInt(dto.get("virtualViews"), 0));
        product.setStatus(toInt(dto.get("status"), 1));
        product.setIsHot(toInt(dto.get("isHot"), 0));
        product.setIsNew(toInt(dto.get("isNew"), 1));
        product.setSort(toInt(dto.get("sort"), 0));
        product.setIsWholesale(toInt(dto.get("isWholesale"), 0));

        productMapper.insert(product);
        Long productId = product.getId();

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> wholesalePrices = (List<Map<String, Object>>) dto.get("wholesalePrices");
        if (wholesalePrices != null) {
            int s = 0;
            for (Map<String, Object> wp : wholesalePrices) {
                ProductWholesale pw = new ProductWholesale();
                pw.setProductId(productId);
                pw.setMinQuantity(toInt(wp.get("minQuantity"), 0));
                pw.setMaxQuantity(toInt(wp.get("maxQuantity"), -1));
                pw.setPrice(toBigDecimal(wp.get("price")));
                pw.setSort(s++);
                wholesaleMapper.insert(pw);
            }
        }

        return productId;
    }

    private Long toLong(Object val) {
        if (val == null) return null;
        if (val instanceof Number) return ((Number) val).longValue();
        try { return Long.parseLong(val.toString()); } catch (Exception e) { return null; }
    }

    private Integer toInt(Object val, Integer def) {
        if (val == null) return def;
        if (val instanceof Number) return ((Number) val).intValue();
        try { return Integer.parseInt(val.toString()); } catch (Exception e) { return def; }
    }

    private BigDecimal toBigDecimal(Object val) {
        if (val == null) return null;
        if (val instanceof BigDecimal) return (BigDecimal) val;
        try { return new BigDecimal(val.toString()); } catch (Exception e) { return null; }
    }
}
