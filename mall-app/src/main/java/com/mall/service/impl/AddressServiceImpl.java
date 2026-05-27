package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.mall.common.exception.BizException;
import com.mall.entity.MallUserAddress;
import com.mall.mapper.MallUserAddressMapper;
import com.mall.service.AddressService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class AddressServiceImpl implements AddressService {

    private final MallUserAddressMapper addressMapper;

    @Override
    public List<Map<String, Object>> list(Long userId) {
        String partyId = userId.toString();
        List<MallUserAddress> list = addressMapper.selectList(
            new QueryWrapper<MallUserAddress>()
                .eq("party_id", partyId)
                .eq("status", 1)
                .orderByDesc("is_default"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallUserAddress addr : list) {
            result.add(toMap(addr));
        }
        return result;
    }

    @Override
    public Map<String, Object> detail(Long userId, String uuid) {
        String partyId = userId.toString();
        MallUserAddress addr = addressMapper.selectOne(
            new QueryWrapper<MallUserAddress>()
                .eq("uuid", uuid).eq("party_id", partyId));
        if (addr == null) throw new BizException("地址不存在");
        return toMap(addr);
    }

    @Override
    @Transactional
    public void add(Long userId, Map<String, Object> dto) {
        String partyId = userId.toString();
        long count = addressMapper.selectCount(
            new QueryWrapper<MallUserAddress>().eq("party_id", partyId).eq("status", 1));
        if (count >= 20) throw new BizException("最多保存20个地址");

        MallUserAddress addr = new MallUserAddress();
        addr.setUuid(UUID.randomUUID().toString().replace("-", ""));
        addr.setPartyId(partyId);
        addr.setReceiverName((String) dto.get("receiverName"));
        addr.setReceiverPhone((String) dto.get("receiverPhone"));
        addr.setCountryId((String) dto.getOrDefault("countryId", "CN"));
        addr.setStateId((String) dto.getOrDefault("stateId", ""));
        addr.setCityId((String) dto.getOrDefault("cityId", ""));
        addr.setAddressDetail((String) dto.get("addressDetail"));
        addr.setZipCode((String) dto.getOrDefault("zipCode", ""));
        Integer isDefault = (Integer) dto.getOrDefault("isDefault", 0);
        addr.setIsDefault(isDefault);
        addr.setStatus(1);
        addr.setCreateTime(LocalDateTime.now());
        addr.setUpdateTime(LocalDateTime.now());
        addressMapper.insert(addr);

        if (isDefault == 1) {
            clearOtherDefaults(partyId, addr.getUuid());
        }
    }

    @Override
    @Transactional
    public void update(Long userId, String uuid, Map<String, Object> dto) {
        String partyId = userId.toString();
        MallUserAddress addr = addressMapper.selectOne(
            new QueryWrapper<MallUserAddress>().eq("uuid", uuid).eq("party_id", partyId));
        if (addr == null) throw new BizException("地址不存在");

        if (dto.containsKey("receiverName")) addr.setReceiverName((String) dto.get("receiverName"));
        if (dto.containsKey("receiverPhone")) addr.setReceiverPhone((String) dto.get("receiverPhone"));
        if (dto.containsKey("countryId")) addr.setCountryId((String) dto.get("countryId"));
        if (dto.containsKey("stateId")) addr.setStateId((String) dto.get("stateId"));
        if (dto.containsKey("cityId")) addr.setCityId((String) dto.get("cityId"));
        if (dto.containsKey("addressDetail")) addr.setAddressDetail((String) dto.get("addressDetail"));
        if (dto.containsKey("zipCode")) addr.setZipCode((String) dto.get("zipCode"));
        if (dto.containsKey("isDefault")) {
            Integer isDefault = (Integer) dto.get("isDefault");
            addr.setIsDefault(isDefault);
            if (isDefault == 1) {
                clearOtherDefaults(partyId, uuid);
            }
        }
        addr.setUpdateTime(LocalDateTime.now());
        addressMapper.updateById(addr);
    }

    @Override
    public void delete(Long userId, String uuid) {
        String partyId = userId.toString();
        MallUserAddress addr = addressMapper.selectOne(
            new QueryWrapper<MallUserAddress>().eq("uuid", uuid).eq("party_id", partyId));
        if (addr == null) throw new BizException("地址不存在");
        addr.setStatus(0);
        addr.setUpdateTime(LocalDateTime.now());
        addressMapper.updateById(addr);
    }

    @Override
    @Transactional
    public void setDefault(Long userId, String uuid) {
        String partyId = userId.toString();
        MallUserAddress addr = addressMapper.selectOne(
            new QueryWrapper<MallUserAddress>().eq("uuid", uuid).eq("party_id", partyId));
        if (addr == null) throw new BizException("地址不存在");
        addr.setIsDefault(1);
        addr.setUpdateTime(LocalDateTime.now());
        addressMapper.updateById(addr);
        clearOtherDefaults(partyId, uuid);
    }

    private void clearOtherDefaults(String partyId, String excludeUuid) {
        addressMapper.update(null,
            new UpdateWrapper<MallUserAddress>()
                .eq("party_id", partyId)
                .ne("uuid", excludeUuid)
                .set("is_default", 0));
    }

    private Map<String, Object> toMap(MallUserAddress addr) {
        Map<String, Object> map = new HashMap<>();
        map.put("uuid", addr.getUuid());
        map.put("receiverName", addr.getReceiverName());
        map.put("receiverPhone", addr.getReceiverPhone());
        map.put("countryId", addr.getCountryId());
        map.put("stateId", addr.getStateId());
        map.put("cityId", addr.getCityId());
        map.put("addressDetail", addr.getAddressDetail());
        map.put("zipCode", addr.getZipCode());
        map.put("isDefault", addr.getIsDefault());
        map.put("createTime", addr.getCreateTime());
        return map;
    }
}
