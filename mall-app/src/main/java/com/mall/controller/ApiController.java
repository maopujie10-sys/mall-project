package com.mall.controller;

import com.mall.common.Result;
import com.mall.entity.*;
import com.mall.service.CategoryService;
import com.mall.service.GoodsService;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api")
public class ApiController {

    private final GoodsService goodsService;
    private final CategoryService categoryService;

    public ApiController(GoodsService goodsService, CategoryService categoryService) {
        this.goodsService = goodsService;
        this.categoryService = categoryService;
    }

    @GetMapping("/banners")
    public Result<List<MallBanner>> banners(@RequestParam(defaultValue = "h5") String type) {
        return Result.ok(goodsService.getBanners(type));
    }

    @GetMapping("/categories")
    public Result<List<MallCategory>> categories() {
        return Result.ok(goodsService.getCategories());
    }

    @GetMapping("/category/tree")
    public Result<List<Map<String, Object>>> categoryTree() {
        return Result.ok(categoryService.getTree());
    }

    @GetMapping("/categories/{parentId}/children")
    public Result<List<MallCategory>> subCategories(@PathVariable String parentId) {
        return Result.ok(goodsService.getSubCategories(parentId));
    }

    @GetMapping("/goods/{goodsId}/skus")
    public Result<List<MallGoodsSku>> skus(@PathVariable String goodsId) {
        return Result.ok(goodsService.getSkusByGoodsId(goodsId));
    }

    @GetMapping("/health")
    public Result<Map<String, String>> health() {
        return Result.ok(Map.of("status", "ok", "time", new Date().toString()));
    }
}
