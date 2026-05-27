package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.UserBalanceUtil;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.PromoteService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class PromoteServiceImpl implements PromoteService {

    private final MallOrderRebateMapper rebateMapper;
    private final MallOrdersPrizeMapper prizeMapper;
    private final MallComboMapper comboMapper;
    private final MallComboRecordMapper comboRecordMapper;
    private final MallSellerMapper sellerMapper;
    private final UserMapper userMapper;
    private final UserBalanceMapper userBalanceMapper;

    @Override
    public Map<String, Object> myPromotion(Long userId) {
        Map<String, Object> result = new HashMap<>();
        // Sum rebates earned by this user
        List<MallOrderRebate> rebates = rebateMapper.selectList(
            new QueryWrapper<MallOrderRebate>().eq("party_id", userId.toString()));
        double totalRebate = rebates.stream().mapToDouble(r -> r.getRebateAmount() != null ? r.getRebateAmount() : 0).sum();
        result.put("totalRebate", totalRebate);
        result.put("rebateCount", rebates.size());
        result.put("rebates", rebates.stream().map(r -> {
            Map<String, Object> m = new HashMap<>();
            m.put("uuid", r.getUuid());
            m.put("orderId", r.getOrderId());
            m.put("rebateAmount", r.getRebateAmount());
            m.put("rebateRate", r.getRebateRate());
            m.put("level", r.getLevel());
            m.put("status", r.getStatus());
            m.put("createTime", r.getCreateTime());
            return m;
        }).toList());
        return result;
    }

    @Override
    public Map<String, Object> teamInfo(Long userId) {
        Map<String, Object> result = new HashMap<>();
        // Count team members (users invited by this user)
        List<MallOrderRebate> teamRebates = rebateMapper.selectList(
            new QueryWrapper<MallOrderRebate>().eq("ORDER_PARTY_ID", userId.toString()));
        long teamSize = teamRebates.stream().map(MallOrderRebate::getPartyId).distinct().count();
        double teamRebateTotal = teamRebates.stream().mapToDouble(r -> r.getRebateAmount() != null ? r.getRebateAmount() : 0).sum();
        result.put("teamSize", teamSize);
        result.put("teamRebateTotal", teamRebateTotal);
        result.put("teamRebates", teamRebates.stream().map(r -> {
            Map<String, Object> m = new HashMap<>();
            m.put("partyId", r.getPartyId());
            m.put("rebateAmount", r.getRebateAmount());
            m.put("level", r.getLevel());
            return m;
        }).toList());
        return result;
    }

    @Override
    public Map<String, Object> carView(Long userId) {
        Map<String, Object> result = new HashMap<>();
        // Available combo packages (express car products)
        List<MallCombo> combos = comboMapper.selectList(
            new QueryWrapper<MallCombo>().orderByAsc("amount"));
        result.put("combos", combos.stream().map(c -> {
            Map<String, Object> m = new HashMap<>();
            m.put("uuid", c.getUuid());
            m.put("iconImg", c.getIconImg());
            m.put("promoteNum", c.getPromoteNum());
            m.put("amount", c.getAmount());
            m.put("day", c.getDay());
            m.put("baseAccessNum", c.getBaseAccessNum());
            m.put("autoAccMin", c.getAutoAccMin());
            m.put("autoAccMax", c.getAutoAccMax());
            m.put("accInterval", c.getAccInterval());
            return m;
        }).toList());
        // Check if user already has active combo
        List<MallComboRecord> activeRecords = comboRecordMapper.selectList(
            new QueryWrapper<MallComboRecord>()
                .eq("party_id", userId.toString())
                .gt("stop_time", System.currentTimeMillis() / 1000));
        result.put("hasActive", !activeRecords.isEmpty());
        if (!activeRecords.isEmpty()) {
            MallComboRecord active = activeRecords.get(0);
            result.put("activeCombo", Map.of(
                "name", active.getName() != null ? active.getName() : "",
                "stopTime", active.getStopTime(),
                "promoteNum", active.getPromoteNum()
            ));
        }
        return result;
    }

    @Override
    @Transactional
    public void carBuy(Long userId, String comboId) {
        MallCombo combo = comboMapper.selectById(comboId);
        if (combo == null) throw new BizException("套餐不存在");
        // Check if already has active combo
        List<MallComboRecord> activeRecords = comboRecordMapper.selectList(
            new QueryWrapper<MallComboRecord>()
                .eq("party_id", userId.toString())
                .gt("stop_time", System.currentTimeMillis() / 1000));
        if (!activeRecords.isEmpty()) throw new BizException("您已有生效中的直通车套餐");
        // Check balance
        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (balance == null || UserBalanceUtil.getAvailable(balance).compareTo(combo.getAmount()) < 0)
            throw new BizException("余额不足");
        // Create purchase record
        MallComboRecord record = new MallComboRecord();
        record.setUuid(UUID.randomUUID().toString().replace("-", ""));
        record.setPartyId(userId.toString());
        record.setComboId(comboId);
        record.setPromoteNum(combo.getPromoteNum());
        record.setAmount(combo.getAmount());
        record.setDay(combo.getDay());
        record.setName("直通车-" + combo.getDay() + "天");
        record.setCreateTime(LocalDateTime.now());
        long now = System.currentTimeMillis() / 1000;
        record.setBeginTime(now);
        record.setStopTime(now + combo.getDay() * 86400L);
        record.setBaseAccessNum(combo.getBaseAccessNum());
        record.setAutoAccMin(combo.getAutoAccMin());
        record.setAutoAccMax(combo.getAutoAccMax());
        record.setAccInterval(combo.getAccInterval());
        comboRecordMapper.insert(record);
    }

    @Override
    public List<Map<String, Object>> carHistory(Long userId) {
        List<MallComboRecord> records = comboRecordMapper.selectList(
            new QueryWrapper<MallComboRecord>()
                .eq("party_id", userId.toString())
                .orderByDesc("create_time"));
        return records.stream().map(r -> {
            Map<String, Object> m = new HashMap<>();
            m.put("uuid", r.getUuid());
            m.put("comboId", r.getComboId());
            m.put("name", r.getName());
            m.put("amount", r.getAmount());
            m.put("day", r.getDay());
            m.put("promoteNum", r.getPromoteNum());
            m.put("createTime", r.getCreateTime());
            m.put("beginTime", r.getBeginTime());
            m.put("stopTime", r.getStopTime());
            m.put("isActive", r.getStopTime() != null && r.getStopTime() > System.currentTimeMillis() / 1000);
            return m;
        }).toList();
    }

    @Override
    @Transactional
    public Map<String, Object> receiveBonus(Long userId) {
        // Check for pending prizes/bonuses
        List<MallOrdersPrize> prizes = prizeMapper.selectList(
            new QueryWrapper<MallOrdersPrize>()
                .eq("party_id", userId.toString())
                .eq("profit_status", 0));
        double totalBonus = prizes.stream().mapToDouble(p -> p.getPrizeReal() != null ? p.getPrizeReal() : 0).sum();
        Map<String, Object> result = new HashMap<>();
        result.put("pendingBonus", totalBonus);
        result.put("pendingCount", prizes.size());
        result.put("received", totalBonus > 0);
        return result;
    }

    @Override
    @Transactional
    public Map<String, Object> receiveInviteRewards(Long userId) {
        // Sum invite rewards from rebates where user was the inviter
        List<MallOrderRebate> inviteRebates = rebateMapper.selectList(
            new QueryWrapper<MallOrderRebate>()
                .eq("ORDER_PARTY_ID", userId.toString())
                .eq("status", 0));
        double totalRewards = inviteRebates.stream().mapToDouble(r -> r.getRebateAmount() != null ? r.getRebateAmount() : 0).sum();
        Map<String, Object> result = new HashMap<>();
        result.put("totalRewards", totalRewards);
        result.put("count", inviteRebates.size());
        result.put("received", totalRewards > 0);
        return result;
    }
}
