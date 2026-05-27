package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.MallKeepGoods;
import com.mall.mapper.MallKeepGoodsMapper;
import com.mall.service.KeepGoodsService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class KeepGoodsServiceImpl implements KeepGoodsService {

    private final MallKeepGoodsMapper keepGoodsMapper;

    @Override
    @Transactional
    public void add(Long userId, String sellerGoodsId) {
        String partyId = userId.toString();
        long count = keepGoodsMapper.selectCount(
            new QueryWrapper<MallKeepGoods>()
                .eq("party_id", partyId)
                .eq("seller_goods_id", sellerGoodsId));
        if (count > 0) throw new BizException("已收藏该商品");

        MallKeepGoods kg = new MallKeepGoods();
        kg.setUuid(UUID.randomUUID().toString().replace("-", ""));
        kg.setPartyId(partyId);
        kg.setSellerGoodsId(sellerGoodsId);
        kg.setCreateTime(LocalDateTime.now());
        keepGoodsMapper.insert(kg);
    }

    @Override
    public void remove(Long userId, String sellerGoodsId) {
        String partyId = userId.toString();
        keepGoodsMapper.delete(
            new QueryWrapper<MallKeepGoods>()
                .eq("party_id", partyId)
                .eq("seller_goods_id", sellerGoodsId));
    }

    @Override
    public List<Map<String, Object>> list(Long userId, int page, int pageSize) {
        String partyId = userId.toString();
        Page<MallKeepGoods> p = new Page<>(page, pageSize);
        Page<MallKeepGoods> result = keepGoodsMapper.selectPage(p,
            new QueryWrapper<MallKeepGoods>()
                .eq("party_id", partyId)
                .orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallKeepGoods kg : result.getRecords()) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("uuid", kg.getUuid());
            map.put("partyId", kg.getPartyId());
            map.put("sellerGoodsId", kg.getSellerGoodsId());
            map.put("createTime", kg.getCreateTime());
            list.add(map);
        }
        return list;
    }

    @Override
    public boolean isKept(Long userId, String sellerGoodsId) {
        String partyId = userId.toString();
        return keepGoodsMapper.selectCount(
            new QueryWrapper<MallKeepGoods>()
                .eq("party_id", partyId)
                .eq("seller_goods_id", sellerGoodsId)) > 0;
    }

    @Override
    public long count(Long userId) {
        String partyId = userId.toString();
        return keepGoodsMapper.selectCount(
            new QueryWrapper<MallKeepGoods>().eq("party_id", partyId));
    }
}
