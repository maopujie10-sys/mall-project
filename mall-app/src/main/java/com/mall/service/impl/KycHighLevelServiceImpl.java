package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.exception.BizException;
import com.mall.entity.Kyc;
import com.mall.entity.KycHighLevel;
import com.mall.mapper.KycHighLevelMapper;
import com.mall.mapper.KycMapper;
import com.mall.service.KycHighLevelService;
import com.mall.service.SysParamService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class KycHighLevelServiceImpl implements KycHighLevelService {

    private final KycHighLevelMapper kycHighLevelMapper;
    private final KycMapper kycMapper;
    private final SysParamService sysParamService;

    @Override
    public Map<String, Object> get(Long userId) {
        KycHighLevel entity = kycHighLevelMapper.selectOne(
            new QueryWrapper<KycHighLevel>().eq("user_id", userId).orderByDesc("id").last("LIMIT 1"));
        if (entity == null) return null;

        Kyc kyc = kycMapper.selectOne(
            new QueryWrapper<Kyc>().eq("user_id", userId).orderByDesc("id").last("LIMIT 1"));
        Map<String, Object> result = toMap(entity);
        if (kyc != null) result.put("name", kyc.getRealName());
        return result;
    }

    @Override
    @Transactional
    public void apply(Long userId, Map<String, Object> dto) {
        String workPlace = (String) dto.get("workPlace");
        String homePlace = (String) dto.get("homePlace");
        String relativesName = (String) dto.get("relativesName");
        String relativesRelation = (String) dto.get("relativesRelation");
        String relativesPlace = (String) dto.get("relativesPlace");
        String relativesPhone = (String) dto.get("relativesPhone");

        String error = verify(workPlace, homePlace, relativesName, relativesRelation,
            relativesPlace, relativesPhone);
        if (error != null) throw new BizException(error);

        Kyc kyc = kycMapper.selectOne(
            new QueryWrapper<Kyc>().eq("user_id", userId).orderByDesc("id").last("LIMIT 1"));
        if (kyc == null || kyc.getStatus() != 1)
            throw new BizException("实名认证未通过，无法进行高级认证");

        String checkResult = checkApplyResult(userId);
        if (checkResult != null) throw new BizException(checkResult);

        KycHighLevel entity = new KycHighLevel();
        entity.setUserId(userId);
        entity.setWorkPlace(workPlace);
        entity.setHomePlace(homePlace);
        entity.setRelativesName(relativesName);
        entity.setRelativesRelation(relativesRelation);
        entity.setRelativesPlace(relativesPlace);
        entity.setRelativesPhone(relativesPhone);
        entity.setIdimg1((String) dto.get("idimg1"));
        entity.setIdimg2((String) dto.get("idimg2"));
        entity.setIdimg3((String) dto.get("idimg3"));
        entity.setStatus(1);
        entity.setApplyTime(LocalDateTime.now());
        kycHighLevelMapper.insert(entity);
    }

    @Override
    public String checkApplyResult(Long userId) {
        KycHighLevel exist = kycHighLevelMapper.selectOne(
            new QueryWrapper<KycHighLevel>().eq("user_id", userId).orderByDesc("id").last("LIMIT 1"));
        if (exist == null) return null;
        if (exist.getStatus() == 1) return "高级认证审核中，请勿重复提交";
        if (exist.getStatus() == 2) return "高级认证已通过";
        return null;
    }

    private String verify(String workPlace, String homePlace, String relativesName,
                          String relativesRelation, String relativesPlace, String relativesPhone) {
        if (isBlank(workPlace)) return "工作地址不能为空";
        if (isBlank(homePlace)) return "家庭地址不能为空";

        String projectType = sysParamService.getString("project_type");
        if (isBlank(projectType)) return "系统参数错误";
        if ("EXCHANGE_DELENO".equals(projectType)) return null;

        if (isBlank(relativesName)) return "亲属姓名不能为空";
        if (isBlank(relativesRelation)) return "亲属关系不能为空";
        if (isBlank(relativesPlace)) return "亲属地址不能为空";
        if (isBlank(relativesPhone)) return "亲属电话不能为空";
        return null;
    }

    private Map<String, Object> toMap(KycHighLevel entity) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", entity.getId());
        map.put("userId", entity.getUserId());
        map.put("workPlace", entity.getWorkPlace());
        map.put("homePlace", entity.getHomePlace());
        map.put("relativesName", entity.getRelativesName());
        map.put("relativesRelation", entity.getRelativesRelation());
        map.put("relativesPlace", entity.getRelativesPlace());
        map.put("relativesPhone", entity.getRelativesPhone());
        map.put("idimg1", entity.getIdimg1());
        map.put("idimg2", entity.getIdimg2());
        map.put("idimg3", entity.getIdimg3());
        map.put("status", entity.getStatus());
        map.put("msg", entity.getMsg());
        map.put("applyTime", entity.getApplyTime());
        map.put("operationTime", entity.getOperationTime());
        return map;
    }

    private boolean isBlank(String s) {
        return s == null || s.trim().isEmpty();
    }
}
