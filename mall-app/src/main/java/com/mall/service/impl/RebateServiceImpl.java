package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.MallOrderRebate;
import com.mall.mapper.MallOrderRebateMapper;
import com.mall.service.RebateService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class RebateServiceImpl implements RebateService {

    private final MallOrderRebateMapper rebateMapper;

    @Override
    public Map<String, Object> list(Long userId, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        String partyId = userId.toString();
        Page<MallOrderRebate> pg = new Page<>(p, ps);
        Page<MallOrderRebate> result = rebateMapper.selectPage(pg,
            new QueryWrapper<MallOrderRebate>()
                .eq("party_id", partyId)
                .orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallOrderRebate r : result.getRecords()) {
            Map<String, Object> m = new HashMap<>();
            m.put("uuid", r.getUuid());
            m.put("orderId", r.getOrderId());
            m.put("fromPartyId", r.getFromPartyId());
            m.put("rebateAmount", r.getRebateAmount());
            m.put("rebateRate", r.getRebateRate());
            m.put("level", r.getLevel());
            m.put("status", r.getStatus());
            m.put("createTime", r.getCreateTime());
            list.add(m);
        }
        Map<String, Object> pageResult = new HashMap<>();
        pageResult.put("total", result.getTotal());
        pageResult.put("page", p);
        pageResult.put("pageSize", ps);
        pageResult.put("list", list);
        return pageResult;
    }

    @Override
    public Map<String, Object> detail(Long userId, String uuid) {
        String partyId = userId.toString();
        MallOrderRebate rebate = rebateMapper.selectOne(
            new QueryWrapper<MallOrderRebate>().eq("uuid", uuid).eq("party_id", partyId));
        if (rebate == null) throw new BizException("返利记录不存在");
        Map<String, Object> m = new HashMap<>();
        m.put("uuid", rebate.getUuid());
        m.put("orderId", rebate.getOrderId());
        m.put("fromPartyId", rebate.getFromPartyId());
        m.put("rebateAmount", rebate.getRebateAmount());
        m.put("rebateRate", rebate.getRebateRate());
        m.put("level", rebate.getLevel());
        m.put("status", rebate.getStatus());
        m.put("createTime", rebate.getCreateTime());
        m.put("updateTime", rebate.getUpdateTime());
        return m;
    }

    @Override
    public Map<String, Object> stats(Long userId) {
        String partyId = userId.toString();
        List<MallOrderRebate> all = rebateMapper.selectList(
            new QueryWrapper<MallOrderRebate>().eq("party_id", partyId).eq("status", 1));
        double totalRebate = 0;
        Map<Integer, Double> byLevel = new HashMap<>();
        for (MallOrderRebate r : all) {
            Double amt = r.getRebateAmount() == null ? 0 : r.getRebateAmount();
            totalRebate += amt;
            Integer lv = r.getLevel() == null ? 0 : r.getLevel();
            byLevel.merge(lv, amt, Double::sum);
        }
        Map<String, Object> result = new HashMap<>();
        result.put("totalRebate", totalRebate);
        result.put("totalCount", all.size());
        result.put("byLevel", byLevel);
        return result;
    }
}
