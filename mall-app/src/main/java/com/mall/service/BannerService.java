package com.mall.service;

import com.mall.entity.MallBanner;
import java.util.Map;

public interface BannerService {
    Map<String, Object> list(String type, String imgType, String startTime, String endTime, Integer page, Integer pageSize);
    MallBanner getById(String uuid);
    void save(MallBanner banner);
    void update(MallBanner banner);
    void delete(String uuid);
}
