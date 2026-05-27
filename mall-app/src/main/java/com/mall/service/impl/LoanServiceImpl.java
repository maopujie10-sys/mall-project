package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.LoanService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class LoanServiceImpl implements LoanService {

    private final MallLoanMapper loanMapper;
    private final MallLoanInfoMapper loanInfoMapper;
    private final MallLoanConfigMapper loanConfigMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final BalanceLogMapper balanceLogMapper;

    @Override
    @Transactional
    public void apply(Long userId, Map<String, Object> dto) {
        String partyId = userId.toString();

        MallLoanConfig config = loanConfigMapper.selectOne(
            new QueryWrapper<MallLoanConfig>().last("LIMIT 1"));
        if (config == null) throw new BizException("贷款功能暂未开放");

        double principal = toDouble(dto.get("principal"));
        if (principal < config.getAmountMin() || principal > config.getAmountMax())
            throw new BizException("贷款金额需在" + config.getAmountMin() + "~" + config.getAmountMax() + "之间");

        int limitDay = Integer.parseInt(dto.getOrDefault("limitDay", "30").toString());
        if (!config.getLendableDays().contains(String.valueOf(limitDay)))
            throw new BizException("不支持该贷款期限");

        double rate = config.getRate();
        double interest = principal * rate * (limitDay / 30.0);
        double priAndInt = principal + interest;

        String uuid = UUID.randomUUID().toString().replace("-", "");
        MallLoan loan = new MallLoan();
        loan.setUuid(uuid);
        loan.setPartyId(partyId);
        loan.setAccType(1);
        loan.setUserName((String) dto.getOrDefault("userName", ""));
        loan.setStatus(0);
        loan.setLimitDay(limitDay);
        loan.setPrincipal(principal);
        loan.setRate(rate);
        loan.setInterest(round2(interest));
        loan.setPriAndInt(round2(priAndInt));
        loan.setActual(0.0);
        loan.setSubmitTime(LocalDateTime.now());
        loan.setLoanMethod((Integer) dto.getOrDefault("loanMethod", 1));
        loanMapper.insert(loan);

        MallLoanInfo info = new MallLoanInfo();
        info.setUuid(UUID.randomUUID().toString().replace("-", ""));
        info.setLoanId(uuid);
        info.setRealName((String) dto.getOrDefault("realName", ""));
        info.setIdNumber((String) dto.getOrDefault("idNumber", ""));
        info.setNationality((String) dto.getOrDefault("nationality", ""));
        info.setPhotoFront((String) dto.getOrDefault("photoFront", ""));
        info.setPhotoRear((String) dto.getOrDefault("photoRear", ""));
        info.setPhotoHand((String) dto.getOrDefault("photoHand", ""));
        loanInfoMapper.insert(info);
    }

    @Override
    public Map<String, Object> list(Long userId, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        String partyId = userId.toString();
        Page<MallLoan> pg = new Page<>(p, ps);
        Page<MallLoan> result = loanMapper.selectPage(pg,
            new QueryWrapper<MallLoan>().eq("party_id", partyId).orderByDesc("submit_time"));
        return buildPageResult(result, p, ps);
    }

    @Override
    public Map<String, Object> detail(Long userId, String uuid) {
        String partyId = userId.toString();
        MallLoan loan = loanMapper.selectOne(
            new QueryWrapper<MallLoan>().eq("uuid", uuid).eq("party_id", partyId));
        if (loan == null) throw new BizException("贷款记录不存在");
        MallLoanInfo info = loanInfoMapper.selectOne(
            new QueryWrapper<MallLoanInfo>().eq("loan_id", uuid));
        Map<String, Object> map = toMap(loan);
        if (info != null) {
            map.put("loanInfo", toInfoMap(info));
        }
        return map;
    }

    @Override
    @Transactional
    public void repay(Long userId, String uuid, Map<String, Object> dto) {
        String partyId = userId.toString();
        MallLoan loan = loanMapper.selectOne(
            new QueryWrapper<MallLoan>().eq("uuid", uuid).eq("party_id", partyId));
        if (loan == null) throw new BizException("贷款记录不存在");
        if (loan.getStatus() != 1) throw new BizException("该贷款状态不允许还款");

        double repayAmount = toDouble(dto.get("amount"));
        if (repayAmount <= 0) throw new BizException("还款金额必须大于0");

        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (balance == null) throw new BizException("账户不存在");

        BigDecimal repayBd = BigDecimal.valueOf(repayAmount);
        if (balance.getBalance().compareTo(repayBd) < 0) throw new BizException("余额不足");

        int rows = userBalanceMapper.deductBalance(userId, repayBd, balance.getVersion());
        if (rows == 0) throw new BizException("扣款失败，请重试");

        balanceLogMapper.insert(BalanceLog.builder()
            .userId(userId).amount(repayBd.negate()).type("LOAN_REPAY")
            .remark("贷款还款 " + uuid).createTime(LocalDateTime.now()).build());

        double currentActual = loan.getActual() == null ? 0 : loan.getActual();
        double totalDue = loan.getPriAndInt() == null ? loan.getPrincipal() : loan.getPriAndInt();
        double newActual = currentActual + repayAmount;
        loan.setActual(round2(newActual));
        loan.setLastPayTime(LocalDateTime.now());
        if (newActual >= totalDue - 0.01) {
            loan.setStatus(3);
        }
        loanMapper.updateById(loan);
    }

    @Override
    public Map<String, Object> config() {
        MallLoanConfig config = loanConfigMapper.selectOne(
            new QueryWrapper<MallLoanConfig>().last("LIMIT 1"));
        if (config == null) return Collections.emptyMap();
        Map<String, Object> map = new HashMap<>();
        map.put("amountMin", config.getAmountMin());
        map.put("amountMax", config.getAmountMax());
        map.put("rate", config.getRate());
        map.put("defaultRate", config.getDefaultRate());
        map.put("lendableDays", config.getLendableDays());
        return map;
    }

    @Override
    public Map<String, Object> adminList(String keyword, Integer status, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallLoan> qw = new QueryWrapper<>();
        if (status != null) qw.eq("status", status);
        if (keyword != null && !keyword.isEmpty())
            qw.and(w -> w.like("user_name", keyword).or().like("party_id", keyword));
        qw.orderByDesc("submit_time");
        Page<MallLoan> pg = new Page<>(p, ps);
        Page<MallLoan> result = loanMapper.selectPage(pg, qw);
        return buildPageResult(result, p, ps);
    }

    @Override
    @Transactional
    public void audit(Long adminId, String uuid, Map<String, Object> dto) {
        MallLoan loan = loanMapper.selectById(uuid);
        if (loan == null) throw new BizException("贷款记录不存在");
        if (loan.getStatus() != 0) throw new BizException("该贷款已审核");

        int status = Integer.parseInt(dto.get("status").toString());
        if (status == 1) {
            loan.setStatus(1);
            // Credit the loan principal to user balance
            Long uid = Long.valueOf(loan.getPartyId());
            userBalanceMapper.addBalance(uid, BigDecimal.valueOf(loan.getPrincipal()));
            balanceLogMapper.insert(BalanceLog.builder()
                .userId(uid).amount(BigDecimal.valueOf(loan.getPrincipal()))
                .type("LOAN_GRANT").remark("贷款放款 " + uuid)
                .createTime(LocalDateTime.now()).build());
        } else if (status == 2) {
            loan.setStatus(2);
            loan.setReject((String) dto.getOrDefault("reject", "审核未通过"));
        } else {
            throw new BizException("无效的审核状态");
        }
        loan.setAuditTime(LocalDateTime.now());
        loanMapper.updateById(loan);
    }

    @Override
    public void saveConfig(Map<String, Object> dto) {
        MallLoanConfig config = loanConfigMapper.selectOne(
            new QueryWrapper<MallLoanConfig>().last("LIMIT 1"));
        if (config == null) {
            config = new MallLoanConfig();
            config.setUuid(UUID.randomUUID().toString().replace("-", ""));
        }
        config.setAmountMin(toDouble(dto.getOrDefault("amountMin", 100)));
        config.setAmountMax(toDouble(dto.getOrDefault("amountMax", 10000)));
        config.setRate(toDouble(dto.getOrDefault("rate", 0.05)));
        config.setDefaultRate(toDouble(dto.getOrDefault("defaultRate", 0.001)));
        config.setLendableDays((String) dto.getOrDefault("lendableDays", "7,14,30,90"));
        config.setAllLendableDays((String) dto.getOrDefault("allLendableDays", "7,14,30,90,180,360"));
        if (config.getUuid() != null && loanConfigMapper.selectById(config.getUuid()) != null) {
            loanConfigMapper.updateById(config);
        } else {
            loanConfigMapper.insert(config);
        }
    }

    @Override
    public Map<String, Object> configList() {
        List<MallLoanConfig> list = loanConfigMapper.selectList(null);
        return Map.of("list", list);
    }

    private Map<String, Object> buildPageResult(Page<MallLoan> result, int p, int ps) {
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallLoan l : result.getRecords()) list.add(toMap(l));
        Map<String, Object> r = new HashMap<>();
        r.put("total", result.getTotal());
        r.put("page", p);
        r.put("pageSize", ps);
        r.put("list", list);
        return r;
    }

    private Map<String, Object> toMap(MallLoan l) {
        Map<String, Object> m = new HashMap<>();
        m.put("uuid", l.getUuid());
        m.put("partyId", l.getPartyId());
        m.put("accType", l.getAccType());
        m.put("userName", l.getUserName());
        m.put("status", l.getStatus());
        m.put("limitDay", l.getLimitDay());
        m.put("principal", l.getPrincipal());
        m.put("rate", l.getRate());
        m.put("interest", l.getInterest());
        m.put("priAndInt", l.getPriAndInt());
        m.put("actual", l.getActual());
        m.put("reject", l.getReject());
        m.put("loanMethod", l.getLoanMethod());
        m.put("submitTime", l.getSubmitTime());
        m.put("auditTime", l.getAuditTime());
        m.put("lastPayTime", l.getLastPayTime());
        return m;
    }

    private Map<String, Object> toInfoMap(MallLoanInfo info) {
        Map<String, Object> m = new HashMap<>();
        m.put("realName", info.getRealName());
        m.put("idNumber", info.getIdNumber());
        m.put("nationality", info.getNationality());
        m.put("photoFront", info.getPhotoFront());
        m.put("photoRear", info.getPhotoRear());
        m.put("photoHand", info.getPhotoHand());
        return m;
    }

    private double toDouble(Object v) {
        if (v instanceof Number) return ((Number) v).doubleValue();
        return Double.parseDouble(v.toString());
    }

    private double round2(double v) {
        return BigDecimal.valueOf(v).setScale(2, RoundingMode.HALF_UP).doubleValue();
    }
}
