package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mall.entity.MallBanner;
import com.mall.entity.MallCategory;
import com.mall.entity.MallGoodsSku;
import com.mall.mapper.MallBannerMapper;
import com.mall.mapper.MallCategoryMapper;
import com.mall.mapper.MallGoodsSkuMapper;
import com.mall.service.GoodsService;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class GoodsServiceImpl implements GoodsService {

    private final MallBannerMapper bannerMapper;
    private final MallCategoryMapper categoryMapper;
    private final MallGoodsSkuMapper goodsSkuMapper;

    public GoodsServiceImpl(MallBannerMapper bannerMapper,
                            MallCategoryMapper categoryMapper,
                            MallGoodsSkuMapper goodsSkuMapper) {
        this.bannerMapper = bannerMapper;
        this.categoryMapper = categoryMapper;
        this.goodsSkuMapper = goodsSkuMapper;
    }

    @Override
    public List<MallBanner> getBanners(String type) {
        LambdaQueryWrapper<MallBanner> qw = new LambdaQueryWrapper<>();
        qw.eq(MallBanner::getType, type);
        qw.orderByAsc(MallBanner::getSort);
        List<MallBanner> banners = bannerMapper.selectList(qw);
        if (banners == null || banners.isEmpty()) {
            return getDefaultBanners(type);
        }
        return banners;
    }

    private List<MallBanner> getDefaultBanners(String type) {
        MallBanner banner = new MallBanner();
        banner.setUuid("default-" + type);
        banner.setImgUrl("https://img.tiktook.eu.cc/default/banner-" + type + ".jpg");
        banner.setSort(1);
        banner.setType(type);
        banner.setLink("");
        return List.of(banner);
    }

    @Override
    public List<MallCategory> getCategories() {
        LambdaQueryWrapper<MallCategory> qw = new LambdaQueryWrapper<>();
        qw.eq(MallCategory::getStatus, 1);
        qw.orderByAsc(MallCategory::getSort);
        return categoryMapper.selectList(qw);
    }

    @Override
    public List<MallCategory> getSubCategories(String parentId) {
        LambdaQueryWrapper<MallCategory> qw = new LambdaQueryWrapper<>();
        qw.eq(MallCategory::getParentId, parentId);
        qw.eq(MallCategory::getStatus, 1);
        qw.orderByAsc(MallCategory::getSort);
        return categoryMapper.selectList(qw);
    }

    @Override
    public List<MallGoodsSku> getSkusByGoodsId(String goodsId) {
        LambdaQueryWrapper<MallGoodsSku> qw = new LambdaQueryWrapper<>();
        qw.eq(MallGoodsSku::getGoodId, goodsId);
        qw.eq(MallGoodsSku::getDeleted, 0);
        return goodsSkuMapper.selectList(qw);
    }
}
