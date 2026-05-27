package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.MallFocusSeller;
import com.mall.mapper.MallFocusSellerMapper;
import com.mall.service.FocusSellerService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class FocusSellerServiceImpl implements FocusSellerService {

    private final MallFocusSellerMapper focusSellerMapper;

    @Override
    @Transactional
    public void follow(Long userId, String sellerId) {
        String partyId = userId.toString();
        long count = focusSellerMapper.selectCount(
            new QueryWrapper<MallFocusSeller>()
                .eq("party_id", partyId)
                .eq("seller_id", sellerId));
        if (count > 0) throw new BizException("已关注该商家");

        MallFocusSeller fs = new MallFocusSeller();
        fs.setUuid(UUID.randomUUID().toString().replace("-", ""));
        fs.setPartyId(partyId);
        fs.setSellerId(sellerId);
        fs.setCreateTime(LocalDateTime.now());
        focusSellerMapper.insert(fs);
    }

    @Override
    public void unfollow(Long userId, String sellerId) {
        String partyId = userId.toString();
        focusSellerMapper.delete(
            new QueryWrapper<MallFocusSeller>()
                .eq("party_id", partyId)
                .eq("seller_id", sellerId));
    }

    @Override
    public List<Map<String, Object>> list(Long userId, int page, int pageSize) {
        String partyId = userId.toString();
        Page<MallFocusSeller> p = new Page<>(page, pageSize);
        Page<MallFocusSeller> result = focusSellerMapper.selectPage(p,
            new QueryWrapper<MallFocusSeller>()
                .eq("party_id", partyId)
                .orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallFocusSeller fs : result.getRecords()) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("uuid", fs.getUuid());
            map.put("partyId", fs.getPartyId());
            map.put("sellerId", fs.getSellerId());
            map.put("createTime", fs.getCreateTime());
            list.add(map);
        }
        return list;
    }

    @Override
    public boolean isFollowed(Long userId, String sellerId) {
        String partyId = userId.toString();
        return focusSellerMapper.selectCount(
            new QueryWrapper<MallFocusSeller>()
                .eq("party_id", partyId)
                .eq("seller_id", sellerId)) > 0;
    }

    @Override
    public long count(Long userId) {
        String partyId = userId.toString();
        return focusSellerMapper.selectCount(
            new QueryWrapper<MallFocusSeller>().eq("party_id", partyId));
    }
}
