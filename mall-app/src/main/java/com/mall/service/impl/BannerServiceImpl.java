package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.entity.MallBanner;
import com.mall.mapper.MallBannerMapper;
import com.mall.service.BannerService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.HashMap;

@Service
@RequiredArgsConstructor
public class BannerServiceImpl implements BannerService {

    private final MallBannerMapper bannerMapper;

    @Override
    public Map<String, Object> list(String type, String imgType, String startTime, String endTime, Integer page, Integer pageSize) {
        LambdaQueryWrapper<MallBanner> qw = new LambdaQueryWrapper<>();
        if (StringUtils.hasText(type)) {
            qw.eq(MallBanner::getType, type);
        }
        if (StringUtils.hasText(imgType)) {
            qw.eq(MallBanner::getImgType, Integer.valueOf(imgType));
        }
        if (StringUtils.hasText(startTime)) {
            qw.ge(MallBanner::getCreateTime, LocalDateTime.parse(startTime.replace(" ", "T")));
        }
        if (StringUtils.hasText(endTime)) {
            qw.le(MallBanner::getCreateTime, LocalDateTime.parse(endTime.replace(" ", "T")));
        }
        qw.orderByAsc(MallBanner::getSort);
        IPage<MallBanner> result = bannerMapper.selectPage(new Page<>(page, pageSize), qw);
        Map<String, Object> map = new HashMap<>();
        map.put("records", result.getRecords());
        map.put("total", result.getTotal());
        map.put("page", result.getCurrent());
        map.put("pageSize", result.getSize());
        return map;
    }

    @Override
    public MallBanner getById(String uuid) {
        return bannerMapper.selectById(uuid);
    }

    @Override
    public void save(MallBanner banner) {
        if (banner.getCreateTime() == null) {
            banner.setCreateTime(LocalDateTime.now());
        }
        bannerMapper.insert(banner);
    }

    @Override
    public void update(MallBanner banner) {
        bannerMapper.updateById(banner);
    }

    @Override
    public void delete(String uuid) {
        bannerMapper.deleteById(uuid);
    }
}
