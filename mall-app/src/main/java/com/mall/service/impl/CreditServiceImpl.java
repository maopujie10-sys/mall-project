package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.BalanceLog;
import com.mall.entity.MallCredit;
import com.mall.entity.UserBalance;
import com.mall.mapper.BalanceLogMapper;
import com.mall.mapper.MallCreditMapper;
import com.mall.mapper.UserBalanceMapper;
import com.mall.service.CreditService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class CreditServiceImpl implements CreditService {

    private final MallCreditMapper creditMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final BalanceLogMapper balanceLogMapper;

    /** 默认月利率5% */
    private static final double DEFAULT_CREDIT_RATE = 0.05;
    /** 默认逾期日利率0.1% */
    private static final double DEFAULT_DEFAULT_RATE = 0.001;

    @Override
    @Transactional
    public void apply(Long userId, Map<String, Object> dto) {
        String partyId = userId.toString();

        double applyAmount = toDouble(dto.get("applyAmount"));
        if (applyAmount <= 0) throw new BizException("申请金额必须大于0");

        int creditPeriod = (Integer) dto.getOrDefault("creditPeriod", 1);
        if (creditPeriod < 1 || creditPeriod > 12) throw new BizException("贷款期限1-12个月");

        double creditRate = DEFAULT_CREDIT_RATE;
        if (dto.containsKey("creditRate")) {
            creditRate = toDouble(dto.get("creditRate"));
        }

        double totalInterest = applyAmount * creditRate * creditPeriod;
        double totalRepayment = applyAmount + totalInterest;

        MallCredit credit = new MallCredit();
        credit.setUuid(UUID.randomUUID().toString().replace("-", ""));
        credit.setPartyId(partyId);
        credit.setStatus(0);
        credit.setRealName((String) dto.getOrDefault("realName", ""));
        credit.setIdentification((String) dto.getOrDefault("identification", ""));
        credit.setCountryId((Integer) dto.getOrDefault("countryId", 0));
        credit.setImgCertificateFace((String) dto.getOrDefault("imgCertificateFace", ""));
        credit.setImgCertificateBack((String) dto.getOrDefault("imgCertificateBack", ""));
        credit.setImgCertificateHand((String) dto.getOrDefault("imgCertificateHand", ""));
        credit.setCreditPeriod(creditPeriod);
        credit.setApplyAmount(applyAmount);
        credit.setCreditRate(creditRate);
        credit.setDefaultRate(DEFAULT_DEFAULT_RATE);
        credit.setTotalInterest(round2(totalInterest));
        credit.setTotalRepayment(round2(totalRepayment));
        credit.setActualRepayment(0.0);
        credit.setCustomerSubmitTime(LocalDateTime.now());
        creditMapper.insert(credit);
    }

    @Override
    public List<Map<String, Object>> list(Long userId) {
        String partyId = userId.toString();
        List<MallCredit> list = creditMapper.selectList(
            new QueryWrapper<MallCredit>()
                .eq("party_id", partyId)
                .orderByDesc("customer_submit_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallCredit c : list) {
            result.add(toMap(c));
        }
        return result;
    }

    @Override
    public Map<String, Object> detail(Long userId, String uuid) {
        String partyId = userId.toString();
        MallCredit credit = creditMapper.selectOne(
            new QueryWrapper<MallCredit>().eq("uuid", uuid).eq("party_id", partyId));
        if (credit == null) throw new BizException("贷款记录不存在");
        return toMap(credit);
    }

    @Override
    @Transactional
    public void repay(Long userId, String uuid, Map<String, Object> dto) {
        String partyId = userId.toString();
        MallCredit credit = creditMapper.selectOne(
            new QueryWrapper<MallCredit>().eq("uuid", uuid).eq("party_id", partyId));
        if (credit == null) throw new BizException("贷款记录不存在");
        if (credit.getStatus() != 1) throw new BizException("该贷款状态不允许还款");

        double repayAmount = toDouble(dto.get("amount"));
        if (repayAmount <= 0) throw new BizException("还款金额必须大于0");

        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (balance == null) throw new BizException("账户不存在");

        BigDecimal repayBd = BigDecimal.valueOf(repayAmount);
        if (balance.getBalance().compareTo(repayBd) < 0) throw new BizException("余额不足");

        int rows = userBalanceMapper.deductBalance(userId, repayBd, balance.getVersion());
        if (rows == 0) throw new BizException("扣款失败，请重试");

        BalanceLog log = BalanceLog.builder()
            .userId(userId)
            .amount(repayBd.negate())
            .type("REPAY")
            .remark("贷款还款 " + uuid)
            .relatedId(null)
            .createTime(LocalDateTime.now())
            .build();
        balanceLogMapper.insert(log);

        double currentActual = credit.getActualRepayment() == null ? 0 : credit.getActualRepayment();
        double totalRepay = credit.getTotalRepayment() == null ? credit.getApplyAmount() : credit.getTotalRepayment();
        double newActual = currentActual + repayAmount;
        credit.setActualRepayment(round2(newActual));
        if (newActual >= totalRepay - 0.01) {
            credit.setStatus(2);
            credit.setFinalRepayTime(LocalDateTime.now());
        }
        creditMapper.updateById(credit);
    }

    private Map<String, Object> toMap(MallCredit c) {
        Map<String, Object> map = new HashMap<>();
        map.put("uuid", c.getUuid());
        map.put("status", c.getStatus());
        map.put("realName", c.getRealName());
        map.put("identification", c.getIdentification());
        map.put("countryId", c.getCountryId());
        map.put("creditPeriod", c.getCreditPeriod());
        map.put("applyAmount", c.getApplyAmount());
        map.put("creditRate", c.getCreditRate());
        map.put("defaultRate", c.getDefaultRate());
        map.put("totalInterest", c.getTotalInterest());
        map.put("totalRepayment", c.getTotalRepayment());
        map.put("actualRepayment", c.getActualRepayment());
        map.put("rejectReason", c.getRejectReason());
        map.put("customerSubmitTime", c.getCustomerSubmitTime());
        map.put("systemAuditTime", c.getSystemAuditTime());
        map.put("finalRepayTime", c.getFinalRepayTime());
        map.put("expireTime", c.getExpireTime());
        return map;
    }

    @Override
    public Map<String, Object> adminCreditList(String userCode, String userName, String identification,
                                                Integer status, String startTime, String endTime, Integer pageNum, Integer pageSize) {
        return Map.of("total", 0L, "list", List.of());
    }

    @Override
    @Transactional
    public void adminCreditPass(String creditId, String safeword, String operator) {
        MallCredit credit = creditMapper.selectById(creditId);
        if (credit == null) throw new BizException("贷款记录不存在");
        credit.setStatus(1);
        credit.setSystemAuditTime(LocalDateTime.now());
        creditMapper.updateById(credit);
    }

    @Override
    @Transactional
    public void adminCreditOperate(String creditId, String operateType, String rejectReason,
                                    String manualRepay, String safeword, String operator) {
        MallCredit credit = creditMapper.selectById(creditId);
        if (credit == null) throw new BizException("贷款记录不存在");
        // approve/reject/manualRepay handled by admin via Agent
        throw new BizException("功能暂未开放，请通过AI总后台操作");
    }

    private double toDouble(Object v) {
        if (v instanceof Number) return ((Number) v).doubleValue();
        return Double.parseDouble(v.toString());
    }

    private double round2(double v) {
        return BigDecimal.valueOf(v).setScale(2, RoundingMode.HALF_UP).doubleValue();
    }
}
