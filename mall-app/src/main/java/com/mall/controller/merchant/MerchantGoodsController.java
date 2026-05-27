package com.mall.controller.merchant;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.Result;
import com.mall.entity.Category;
import com.mall.entity.Product;
import com.mall.entity.ProductSku;
import com.mall.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 商家端-商品管理（迁移自旧商城 SellerGoodsController 商家自有功能）
 * 高级搜索/分类统计/SKU详情/批量排序
 */
@RestController
@RequestMapping("/merchant")
@RequiredArgsConstructor
public class MerchantGoodsController {

    private final ProductMapper productMapper;
    private final ProductSkuMapper skuMapper;
    private final ProductImageMapper productImageMapper;
    private final CategoryMapper categoryMapper;

    /**
     * 商家自有商品高级搜索（含价格区间、分类筛选、新品/热销筛选）
     */
    @GetMapping("/my-goods/search")
    public Result<?> searchMyGoods(@RequestAttribute Long userId,
                                   @RequestParam(defaultValue = "1") Integer pageNum,
                                   @RequestParam(defaultValue = "10") Integer pageSize,
                                   @RequestParam(required = false) String keyword,
                                   @RequestParam(required = false) Long categoryId,
                                   @RequestParam(required = false) Integer isNew,
                                   @RequestParam(required = false) Integer isHot,
                                   @RequestParam(required = false) Integer status,
                                   @RequestParam(required = false) BigDecimal priceMin,
                                   @RequestParam(required = false) BigDecimal priceMax) {

        QueryWrapper<Product> qw = new QueryWrapper<>();
        qw.eq("merchant_id", userId);
        qw.eq("deleted", 0);

        if (status != null) qw.eq("status", status);
        if (categoryId != null) qw.eq("category_id", categoryId);
        if (isNew != null) qw.eq("is_new", isNew);
        if (isHot != null) qw.eq("is_hot", isHot);
        if (keyword != null && !keyword.isBlank()) {
            qw.and(w -> w.like("name", keyword).or().like("subtitle", keyword));
        }
        if (priceMin != null) qw.ge("price", priceMin);
        if (priceMax != null) qw.le("price", priceMax);
        qw.orderByDesc("sort", "create_time");

        Page<Product> page = new Page<>(pageNum, pageSize);
        Page<Product> result = productMapper.selectPage(page, qw);

        List<Map<String, Object>> list = result.getRecords().stream().map(p -> {
            Map<String, Object> m = new HashMap<>();
            m.put("id", p.getId());
            m.put("name", p.getName());
            m.put("subtitle", p.getSubtitle());
            m.put("mainImage", p.getMainImage());
            m.put("price", p.getPrice());
            m.put("originalPrice", p.getOriginalPrice());
            m.put("costPrice", p.getCostPrice());
            m.put("totalStock", p.getTotalStock());
            m.put("sales", p.getSales());
            m.put("virtualSales", p.getVirtualSales());
            m.put("status", p.getStatus());
            m.put("isHot", p.getIsHot());
            m.put("isNew", p.getIsNew());
            m.put("sort", p.getSort());
            m.put("categoryId", p.getCategoryId());
            m.put("createTime", p.getCreateTime());
            return m;
        }).collect(Collectors.toList());

        Map<String, Object> data = new HashMap<>();
        data.put("pageInfo", Map.of("pageNum", pageNum, "pageSize", pageSize, "totalElements", result.getTotal()));
        data.put("pageList", list);
        return Result.ok(data);
    }

    /**
     * 按分类统计商家商品数量
     */
    @GetMapping("/my-goods/category-count")
    public Result<?> categoryGoodsCount(@RequestAttribute Long userId) {
        QueryWrapper<Product> qw = new QueryWrapper<>();
        qw.select("category_id, count(*) as cnt");
        qw.eq("merchant_id", userId);
        qw.eq("deleted", 0);
        qw.eq("status", 1);
        qw.groupBy("category_id");

        List<Map<String, Object>> rawList = productMapper.selectMaps(qw);
        List<Map<String, Object>> result = new ArrayList<>();

        for (Map<String, Object> row : rawList) {
            Map<String, Object> item = new HashMap<>();
            Long catId = (Long) row.get("category_id");
            item.put("categoryId", catId);
            item.put("count", row.get("cnt"));

            if (catId != null) {
                Category cat = categoryMapper.selectById(String.valueOf(catId));
                item.put("categoryName", cat != null ? cat.getName() : "");
                item.put("parentId", cat != null ? cat.getParentId() : "0");
            }
            result.add(item);
        }

        return Result.ok(result);
    }

    /**
     * 商品SKU列表（增强版，含规格属性）
     */
    @GetMapping("/my-goods/{productId}/skus-detail")
    public Result<?> skusDetail(@RequestAttribute Long userId, @PathVariable Long productId) {
        Product product = productMapper.selectById(productId);
        if (product == null || !product.getMerchantId().equals(userId)) {
            return Result.fail("商品不存在或不属于当前商家");
        }

        QueryWrapper<ProductSku> qw = new QueryWrapper<>();
        qw.eq("good_id", String.valueOf(productId));
        qw.orderByAsc("sale");
        List<ProductSku> skus = skuMapper.selectList(qw);

        List<Map<String, Object>> list = skus.stream().map(sku -> {
            Map<String, Object> m = new HashMap<>();
            m.put("id", sku.getId());
            m.put("price", sku.getPrice());
            m.put("promotionPrice", sku.getPromotionPrice());
            m.put("pic", sku.getPic());
            m.put("coverImg", sku.getCoverImg());
            m.put("sale", sku.getSale());
            m.put("spData", sku.getSpData());
            return m;
        }).collect(Collectors.toList());

        Map<String, Object> data = new HashMap<>();
        data.put("productId", productId);
        data.put("productName", product.getName());
        data.put("skus", list);
        return Result.ok(data);
    }

    /**
     * 批量更新商品排序
     */
    @PutMapping("/my-goods/batch-sort")
    public Result<?> batchSort(@RequestAttribute Long userId, @RequestBody List<Map<String, Object>> items) {
        for (Map<String, Object> item : items) {
            Long productId = Long.valueOf(item.get("productId").toString());
            Integer sort = Integer.valueOf(item.get("sort").toString());

            Product product = productMapper.selectById(productId);
            if (product != null && product.getMerchantId().equals(userId)) {
                product.setSort(sort);
                productMapper.updateById(product);
            }
        }
        return Result.ok();
    }
}
