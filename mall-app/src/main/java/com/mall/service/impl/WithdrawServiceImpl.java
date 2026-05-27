package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.OrderNoUtil;
import com.mall.common.UserBalanceUtil;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.TelegramService;
import com.mall.service.SysParamService;
import com.mall.service.WithdrawService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class WithdrawServiceImpl implements WithdrawService {

    private final WithdrawOrderMapper withdrawMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final BalanceLogMapper balanceLogMapper;
    private final TelegramService telegramService;
    private final SysParamService sysParamService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Map<String, Object> apply(Long userId, BigDecimal amount, String usdtAddress) {
        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (balance == null)
            throw new BizException("余额账户不存在");
        BigDecimal available = UserBalanceUtil.getAvailable(balance);
        if (available.compareTo(amount) < 0)
            throw new BizException("可用余额不足");

        int rows = userBalanceMapper.freezeBalance(userId, amount, balance.getVersion());
        if (rows == 0) throw new BizException("余额冻结失败（并发竞争），请重试");

        WithdrawOrder order = WithdrawOrder.builder()
            .orderNo(OrderNoUtil.generateWithdrawNo())
            .userId(userId).amount(amount)
            .usdtAddress(usdtAddress).status(0).build();
        withdrawMapper.insert(order);

        balanceLogMapper.insert(BalanceLog.builder()
            .userId(userId).amount(amount.negate())
            .type("WITHDRAW_APPLY").remark("提现申请冻结").build());

        return Map.of("id", order.getId(), "orderNo", order.getOrderNo());
    }

    @Override
    public List<Map<String, Object>> list(Long userId, Integer pageNum, Integer pageSize) {
        IPage<WithdrawOrder> page = withdrawMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<WithdrawOrder>().eq("user_id", userId).orderByDesc("create_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (WithdrawOrder o : page.getRecords()) {
            result.add(Map.of("id", o.getId(), "orderNo", o.getOrderNo(), "amount", o.getAmount(),
                "status", o.getStatus(), "createTime", o.getCreateTime()));
        }
        return result;
    }

    @Override
    public Map<String, Object> getFee(Long userId, String channel) {
        channel = (channel == null || channel.isEmpty()) ? "USDT" : channel;
        double fee = 0;
        if (channel.contains("BTC")) {
            fee = Double.parseDouble(sysParamService.getString("withdraw_other_channel_fee_part_btc", "0"));
        } else if (channel.contains("ETH")) {
            fee = Double.parseDouble(sysParamService.getString("withdraw_other_channel_fee_part_eth", "0"));
        } else if ("bank".equals(channel)) {
            fee = Double.parseDouble(sysParamService.getString("withdraw_other_channel_fee_part_bank", "0"));
        } else {
            fee = Double.parseDouble(sysParamService.getString("withdraw_fee", "0"));
        }
        fee = fee / 100.0;
        return Map.of("fee", BigDecimal.valueOf(fee), "channel", channel);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void audit(Long id, Boolean approved, String txHash, String reason, Long adminId) {
        WithdrawOrder order = withdrawMapper.selectById(id);
        if (order.getStatus() != 0) throw new BizException("该订单已审核");

        if (approved) {
            order.setStatus(1);
            order.setTxHash(txHash);
            userBalanceMapper.deductFrozen(order.getUserId(), order.getAmount());
            balanceLogMapper.insert(BalanceLog.builder()
                .userId(order.getUserId()).amount(order.getAmount().negate())
                .type("WITHDRAW_SUCCESS").remark("提现成功，哈希：" + txHash).build());
            telegramService.notifyUser(order.getUserId(),
                "提现成功！" + order.getAmount() + " USDT，哈希：" + txHash);
        } else {
            order.setStatus(2);
            order.setRejectReason(reason);
            userBalanceMapper.unfreezeBalance(order.getUserId(), order.getAmount());
            balanceLogMapper.insert(BalanceLog.builder()
                .userId(order.getUserId()).amount(order.getAmount())
                .type("WITHDRAW_REJECT").remark("提现被拒，余额已解冻").build());
            telegramService.notifyUser(order.getUserId(), "提现申请被拒绝：" + reason);
        }
        order.setAuditAdminId(adminId);
        order.setAuditTime(LocalDateTime.now());
        withdrawMapper.updateById(order);
    }
}
