package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.Kyc;
import com.mall.mapper.KycMapper;
import com.mall.service.KycService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class KycServiceImpl implements KycService {

    private final KycMapper kycMapper;

    @Override
    @Transactional
    public void submit(Long userId, Map<String, Object> dto) {
        Kyc exist = kycMapper.selectOne(
            new QueryWrapper<Kyc>().eq("user_id", userId));
        if (exist != null && exist.getStatus() != 2) {
            throw new BizException("已有在途审核记录，请勿重复提交");
        }

        Kyc kyc = Kyc.builder()
            .userId(userId)
            .realName((String) dto.get("realName"))
            .nationality((String) dto.getOrDefault("nationality", ""))
            .idCardNo((String) dto.get("idCardNo"))
            .idCardType((String) dto.getOrDefault("idCardType", "ID_CARD"))
            .frontImg((String) dto.get("frontImg"))
            .backImg((String) dto.get("backImg"))
            .handImg((String) dto.get("handImg"))
            .status(0)
            .submitTime(LocalDateTime.now())
            .build();
        kycMapper.insert(kyc);
    }

    @Override
    public Map<String, Object> status(Long userId) {
        Kyc kyc = kycMapper.selectOne(
            new QueryWrapper<Kyc>().eq("user_id", userId).orderByDesc("id").last("LIMIT 1"));
        if (kyc == null) return Map.of("submitted", false);
        Map<String, Object> map = new HashMap<>();
        map.put("submitted", true);
        map.put("realName", kyc.getRealName());
        map.put("idCardNo", maskIdCard(kyc.getIdCardNo()));
        map.put("idCardType", kyc.getIdCardType());
        map.put("status", kyc.getStatus());
        map.put("rejectReason", kyc.getRejectReason());
        map.put("submitTime", kyc.getSubmitTime());
        map.put("auditTime", kyc.getAuditTime());
        return map;
    }

    @Override
    public List<Map<String, Object>> list(Integer pageNum, Integer pageSize, Integer status) {
        QueryWrapper<Kyc> qw = new QueryWrapper<>();
        if (status != null) qw.eq("status", status);
        qw.orderByAsc("status").orderByDesc("submit_time");
        IPage<Kyc> page = kycMapper.selectPage(new Page<>(pageNum, pageSize), qw);
        List<Map<String, Object>> result = new ArrayList<>();
        for (Kyc k : page.getRecords()) {
            Map<String, Object> m = new HashMap<>();
            m.put("id", k.getId());
            m.put("userId", k.getUserId());
            m.put("realName", k.getRealName());
            m.put("idCardNo", maskIdCard(k.getIdCardNo()));
            m.put("idCardType", k.getIdCardType());
            m.put("status", k.getStatus());
            m.put("rejectReason", k.getRejectReason());
            m.put("submitTime", k.getSubmitTime());
            m.put("auditTime", k.getAuditTime());
            result.add(m);
        }
        return result;
    }

    @Override
    @Transactional
    public void audit(Long id, Boolean approved, String reason, Long adminId) {
        Kyc kyc = kycMapper.selectById(id);
        if (kyc == null) throw new BizException("KYC记录不存在");
        if (kyc.getStatus() != 0) throw new BizException("该KYC已审核");

        kyc.setStatus(approved ? 1 : 2);
        if (!approved) kyc.setRejectReason(reason);
        kyc.setAuditAdminId(adminId);
        kyc.setAuditTime(LocalDateTime.now());
        kycMapper.updateById(kyc);
    }

    private String maskIdCard(String idCardNo) {
        if (idCardNo == null || idCardNo.length() < 8) return idCardNo;
        return idCardNo.substring(0, 3) + "****" + idCardNo.substring(idCardNo.length() - 4);
    }
}
