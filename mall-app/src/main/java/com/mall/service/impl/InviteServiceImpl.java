package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.InviteService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class InviteServiceImpl implements InviteService {

    private final MallOrderRebateMapper rebateMapper;
    private final UserMapper userMapper;

    @Override
    public Map<String, Object> inviteInfo(Long userId) {
        Map<String, Object> result = new HashMap<>();
        // Use userId as invite code
        result.put("inviteCode", userId.toString());
        result.put("inviteLink", "/register?inviteCode=" + userId);
        // Count successful invites via rebate records (users who generated rebates for inviter)
        List<MallOrderRebate> inviteRebates = rebateMapper.selectList(
            new QueryWrapper<MallOrderRebate>().eq("ORDER_PARTY_ID", userId.toString()));
        long inviteCount = inviteRebates.stream().map(MallOrderRebate::getPartyId).distinct().count();
        result.put("inviteCount", inviteCount);
        // Total rewards from invites
        double totalRewards = inviteRebates.stream().mapToDouble(r -> r.getRebateAmount() != null ? r.getRebateAmount() : 0).sum();
        result.put("totalRewards", totalRewards);
        return result;
    }

    @Override
    public Map<String, Object> inviteRecords(Long userId, Integer pageNum, Integer pageSize) {
        List<MallOrderRebate> allRebates = rebateMapper.selectList(
            new QueryWrapper<MallOrderRebate>()
                .eq("ORDER_PARTY_ID", userId.toString())
                .orderByDesc("create_time"));
        List<Map<String, Object>> records = allRebates.stream().map(r -> {
            Map<String, Object> m = new HashMap<>();
            m.put("uuid", r.getUuid());
            m.put("orderId", r.getOrderId());
            m.put("partyId", r.getPartyId());
            m.put("rebateAmount", r.getRebateAmount());
            m.put("level", r.getLevel());
            m.put("status", r.getStatus());
            m.put("createTime", r.getCreateTime());
            return m;
        }).toList();
        Map<String, Object> result = new HashMap<>();
        result.put("total", records.size());
        result.put("list", records);
        return result;
    }
}
