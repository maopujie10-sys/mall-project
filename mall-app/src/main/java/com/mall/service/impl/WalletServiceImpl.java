package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.UserBalanceUtil;
import com.mall.common.exception.BizException;
import com.mall.entity.BalanceLog;
import com.mall.entity.UserBalance;
import com.mall.mapper.BalanceLogMapper;
import com.mall.mapper.UserBalanceMapper;
import com.mall.service.WalletService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.*;

@Service
@RequiredArgsConstructor
public class WalletServiceImpl implements WalletService {

    private final BalanceLogMapper balanceLogMapper;
    private final UserBalanceMapper userBalanceMapper;

    @Override
    public Map<String, Object> logs(Long userId, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        Page<BalanceLog> pg = new Page<>(p, ps);
        Page<BalanceLog> result = balanceLogMapper.selectPage(pg,
            new QueryWrapper<BalanceLog>()
                .eq("user_id", userId)
                .orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (BalanceLog log : result.getRecords()) {
            Map<String, Object> m = new HashMap<>();
            m.put("id", log.getId());
            m.put("amount", log.getAmount());
            m.put("type", log.getType());
            m.put("remark", log.getRemark());
            m.put("relatedId", log.getRelatedId());
            m.put("createTime", log.getCreateTime());
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
    public Map<String, Object> balanceDetail(Long userId) {
        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (balance == null) throw new BizException("账户不存在");

        BigDecimal available = UserBalanceUtil.getAvailable(balance);

        Map<String, Object> map = new HashMap<>();
        map.put("balance", balance.getBalance() != null ? balance.getBalance() : BigDecimal.ZERO);
        map.put("frozen", balance.getFrozen() != null ? balance.getFrozen() : BigDecimal.ZERO);
        map.put("available", available);
        map.put("updateTime", balance.getUpdateTime());
        return map;
    }
}
