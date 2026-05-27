package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.OrderNoUtil;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.RechargeService;
import com.mall.service.TelegramService;
import com.mall.service.LotteryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class RechargeServiceImpl implements RechargeService {

    private final RechargeOrderMapper rechargeMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final BalanceLogMapper balanceLogMapper;
    private final TelegramService telegramService;
    private final LotteryService lotteryService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Map<String, Object> apply(Long userId, BigDecimal amount, String usdtAddress, String txHash, String screenshot) {
        if (txHash != null && !txHash.isBlank()) {
            Long count = rechargeMapper.selectCount(
                new QueryWrapper<RechargeOrder>().eq("tx_hash", txHash));
            if (count > 0)
                throw new BizException("该交易哈希已被使用，请勿重复提交");
        }

        RechargeOrder order = RechargeOrder.builder()
            .orderNo(OrderNoUtil.generateRechargeNo())
            .userId(userId).amount(amount)
            .usdtAddress(usdtAddress).txHash(txHash)
            .screenshot(screenshot).status(0).build();
        rechargeMapper.insert(order);
        return Map.of("id", order.getId(), "orderNo", order.getOrderNo());
    }

    @Override
    public List<Map<String, Object>> list(Long userId, Integer pageNum, Integer pageSize) {
        IPage<RechargeOrder> page = rechargeMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<RechargeOrder>().eq("user_id", userId).orderByDesc("create_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (RechargeOrder o : page.getRecords()) {
            result.add(Map.of("id", o.getId(), "orderNo", o.getOrderNo(), "amount", o.getAmount(),
                "status", o.getStatus(), "createTime", o.getCreateTime()));
        }
        return result;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void audit(Long id, Boolean approved, String reason, Long adminId) {
        RechargeOrder order = rechargeMapper.selectById(id);
        if (order.getStatus() != 0) throw new BizException("该订单已审核");

        if (approved) {
            order.setStatus(1);
            userBalanceMapper.addBalance(order.getUserId(), order.getAmount());
            balanceLogMapper.insert(BalanceLog.builder()
                .userId(order.getUserId()).amount(order.getAmount())
                .type("RECHARGE").remark("充值审核通过：" + order.getOrderNo())
                .relatedId(order.getId()).build());
            telegramService.notifyUser(order.getUserId(),
                "充值成功！+" + order.getAmount() + " USDT已到账");
            lotteryService.onRechargeApproved(order.getUserId(), order.getAmount());
        } else {
            order.setStatus(2);
            order.setRejectReason(reason);
            telegramService.notifyUser(order.getUserId(),
                "充值申请被拒绝：" + reason);
        }
        order.setAuditAdminId(adminId);
        order.setAuditTime(LocalDateTime.now());
        rechargeMapper.updateById(order);
    }
}
