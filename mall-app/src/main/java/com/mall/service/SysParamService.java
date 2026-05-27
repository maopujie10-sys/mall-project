package com.mall.service;

import com.mall.entity.SysParam;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

public interface SysParamService {
    SysParam getByKey(String key);
    String getString(String key);
    String getString(String key, String defaultValue);
    Integer getInt(String key);
    BigDecimal getDecimal(String key);
    List<Map<String, Object>> listAll();
    void save(Map<String, Object> dto);
    void update(Long id, Map<String, Object> dto);
    void delete(Long id);
}
