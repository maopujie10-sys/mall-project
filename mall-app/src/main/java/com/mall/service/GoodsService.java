package com.mall.service;

import com.mall.entity.MallBanner;
import com.mall.entity.MallCategory;
import com.mall.entity.MallGoodsSku;

import java.util.List;

public interface GoodsService {
    List<MallBanner> getBanners(String type);
    List<MallCategory> getCategories();
    List<MallCategory> getSubCategories(String parentId);
    List<MallGoodsSku> getSkusByGoodsId(String goodsId);
}
