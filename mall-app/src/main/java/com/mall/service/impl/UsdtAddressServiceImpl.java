package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.exception.BizException;
import com.mall.entity.UsdtAddress;
import com.mall.mapper.UsdtAddressMapper;
import com.mall.service.UsdtAddressService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UsdtAddressServiceImpl implements UsdtAddressService {

    private final UsdtAddressMapper usdtAddressMapper;

    @Override
    public List<UsdtAddress> listByUser(Long userId) {
        return usdtAddressMapper.selectList(
            new QueryWrapper<UsdtAddress>()
                .eq("user_id", userId)
                .orderByDesc("is_active")
                .orderByDesc("create_time"));
    }

    @Override
    public UsdtAddress add(Long userId, String network, String address, String label) {
        Long count = usdtAddressMapper.selectCount(
            new QueryWrapper<UsdtAddress>().eq("user_id", userId));
        if (count >= 5) throw new BizException("最多添加5个地址");

        UsdtAddress entity = new UsdtAddress();
        entity.setUserId(userId);
        entity.setNetwork(network);
        entity.setAddress(address);
        entity.setLabel(label == null ? "" : label);
        entity.setIsActive(count == 0 ? 1 : 0);
        usdtAddressMapper.insert(entity);
        return entity;
    }

    @Override
    public void delete(Long userId, Long id) {
        UsdtAddress addr = usdtAddressMapper.selectById(id);
        if (addr == null || !addr.getUserId().equals(userId))
            throw new BizException("地址不存在");
        usdtAddressMapper.deleteById(id);
    }

    @Override
    public void setActive(Long userId, Long id) {
        UsdtAddress addr = usdtAddressMapper.selectById(id);
        if (addr == null || !addr.getUserId().equals(userId))
            throw new BizException("地址不存在");
        // deactivate all addresses for this user
        List<UsdtAddress> all = usdtAddressMapper.selectList(
            new QueryWrapper<UsdtAddress>().eq("user_id", userId));
        for (UsdtAddress a : all) {
            a.setIsActive(0);
            usdtAddressMapper.updateById(a);
        }
        addr.setIsActive(1);
        usdtAddressMapper.updateById(addr);
    }
}
