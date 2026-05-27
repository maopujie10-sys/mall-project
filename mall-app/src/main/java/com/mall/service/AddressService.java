package com.mall.service;

import java.util.List;
import java.util.Map;

public interface AddressService {
    List<Map<String, Object>> list(Long userId);
    Map<String, Object> detail(Long userId, String uuid);
    void add(Long userId, Map<String, Object> dto);
    void update(Long userId, String uuid, Map<String, Object> dto);
    void delete(Long userId, String uuid);
    void setDefault(Long userId, String uuid);
}
