package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.exception.BizException;
import com.mall.entity.SysParam;
import com.mall.mapper.SysParamMapper;
import com.mall.service.SysParamService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.*;

@Service
@RequiredArgsConstructor
public class SysParamServiceImpl implements SysParamService {

    private final SysParamMapper sysParamMapper;

    @Override
    public SysParam getByKey(String key) {
        SysParam p = sysParamMapper.selectOne(
            new QueryWrapper<SysParam>().eq("param_key", key));
        if (p == null) {
            throw new BizException("参数不存在: " + key);
        }
        return p;
    }

    @Override
    public String getString(String key) {
        return getByKey(key).getParamValue();
    }

    @Override
    public String getString(String key, String defaultValue) {
        SysParam p = sysParamMapper.selectOne(
            new QueryWrapper<SysParam>().eq("param_key", key));
        return p != null ? p.getParamValue() : defaultValue;
    }

    @Override
    public Integer getInt(String key) {
        String v = getString(key);
        try {
            return Integer.parseInt(v);
        } catch (NumberFormatException e) {
            throw new BizException("参数值不是整数: " + key);
        }
    }

    @Override
    public BigDecimal getDecimal(String key) {
        String v = getString(key);
        try {
            return new BigDecimal(v);
        } catch (NumberFormatException e) {
            throw new BizException("参数值不是数字: " + key);
        }
    }

    @Override
    public List<Map<String, Object>> listAll() {
        List<SysParam> list = sysParamMapper.selectList(
            new QueryWrapper<SysParam>().orderByAsc("id"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (SysParam p : list) {
            Map<String, Object> map = new HashMap<>();
            map.put("id", p.getId());
            map.put("paramKey", p.getParamKey());
            map.put("paramValue", p.getParamValue());
            map.put("paramType", p.getParamType());
            map.put("description", p.getDescription());
            map.put("editable", p.getEditable());
            map.put("createTime", p.getCreateTime());
            map.put("updateTime", p.getUpdateTime());
            result.add(map);
        }
        return result;
    }

    @Override
    public void save(Map<String, Object> dto) {
        String key = (String) dto.get("paramKey");
        SysParam exist = sysParamMapper.selectOne(
            new QueryWrapper<SysParam>().eq("param_key", key));
        if (exist != null) {
            throw new BizException("参数键已存在: " + key);
        }
        SysParam p = new SysParam();
        p.setParamKey(key);
        p.setParamValue((String) dto.getOrDefault("paramValue", ""));
        p.setParamType((String) dto.getOrDefault("paramType", "STRING"));
        p.setDescription((String) dto.getOrDefault("description", ""));
        p.setEditable(1);
        sysParamMapper.insert(p);
    }

    @Override
    public void update(Long id, Map<String, Object> dto) {
        SysParam p = sysParamMapper.selectById(id);
        if (p == null) {
            throw new BizException("参数不存在");
        }
        if (dto.containsKey("paramValue")) {
            p.setParamValue((String) dto.get("paramValue"));
        }
        if (dto.containsKey("paramType")) {
            p.setParamType((String) dto.get("paramType"));
        }
        if (dto.containsKey("description")) {
            p.setDescription((String) dto.get("description"));
        }
        sysParamMapper.updateById(p);
    }

    @Override
    public void delete(Long id) {
        SysParam p = sysParamMapper.selectById(id);
        if (p == null) {
            throw new BizException("参数不存在");
        }
        if (p.getEditable() != null && p.getEditable() == 0) {
            throw new BizException("该参数不可删除");
        }
        sysParamMapper.deleteById(id);
    }
}
