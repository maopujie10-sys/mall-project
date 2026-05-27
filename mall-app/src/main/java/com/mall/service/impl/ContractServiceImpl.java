package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.exception.BizException;
import com.mall.entity.SysParam;
import com.mall.mapper.SysParamMapper;
import com.mall.service.ContractService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class ContractServiceImpl implements ContractService {

    private final SysParamMapper sysParamMapper;

    @Override
    public Map<String, Object> contractInfo() {
        Map<String, Object> info = new HashMap<>();
        SysParam enabled = sysParamMapper.selectOne(
            new QueryWrapper<SysParam>().eq("param_key", "contract_enabled"));
        info.put("enabled", enabled != null && "true".equals(enabled.getParamValue()));
        info.put("title", "TikTokMall 电子合同");
        info.put("version", "1.0");
        info.put("description", "本电子合同依据平台规则生成，具有法律效力");
        info.put("clauses", List.of(
            "双方在平等、自愿的基础上，经协商一致，签订本合同",
            "买方同意按照平台公示的价格支付商品价款",
            "卖方保证所售商品符合质量标准",
            "争议解决方式：协商解决，协商不成的提交平台所在地法院管辖"
        ));
        return info;
    }

    @Override
    @Transactional
    public void signContract(Long userId, String contractType, String contractContent) {
        if (contractType == null || contractType.isEmpty()) throw new BizException("合同类型不能为空");
        SysParam record = new SysParam();
        record.setParamKey("contract_signed_" + userId + "_" + System.currentTimeMillis());
        record.setParamValue(contractType + "|" + (contractContent != null ? contractContent : ""));
        record.setDescription("用户签署电子合同");
        record.setCreateTime(LocalDateTime.now());
        sysParamMapper.insert(record);
    }

    @Override
    public List<Map<String, Object>> myContracts(Long userId) {
        List<SysParam> records = sysParamMapper.selectList(
            new QueryWrapper<SysParam>()
                .likeRight("param_key", "contract_signed_" + userId + "_")
                .orderByDesc("create_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (SysParam r : records) {
            Map<String, Object> m = new HashMap<>();
            m.put("id", r.getId());
            String val = r.getParamValue();
            m.put("contractType", val != null && val.contains("|") ? val.split("\\|")[0] : "");
            m.put("signedAt", r.getCreateTime());
            result.add(m);
        }
        return result;
    }
}
