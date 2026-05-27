package com.mall.service;

import java.util.Map;

public interface MallLevelService {
    java.util.List<Map<String, Object>> levelList();
    Map<String, Object> levelDetail(String uuid);
    Map<String, Object> levelConfig();
}
