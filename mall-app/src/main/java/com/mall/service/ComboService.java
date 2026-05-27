package com.mall.service;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

public interface ComboService {
    List<Map<String, Object>> list(String lang);
    Map<String, Object> detail(String uuid, String lang);
    void create(Map<String, Object> dto);
    void update(String uuid, Map<String, Object> dto);
    void delete(String uuid);
    void buy(Long userId, String comboId);
    List<Map<String, Object>> myCombos(Long userId);
    List<Map<String, Object>> myRecords(Long userId, int page, int pageSize);

    // === Admin ===
    Map<String, Object> adminComboList(String name, String startTime, String endTime, Integer page, Integer pageSize);
    void adminComboSave(String name, String iconImg, BigDecimal amount, Integer day, Integer promoteNum,
                        Integer baseAccessNum, Integer autoAccMin, Integer autoAccMax);
    void adminComboUpdate(String uuid, String name, String iconImg, BigDecimal amount, Integer day,
                          Integer promoteNum, Integer baseAccessNum, Integer autoAccMin, Integer autoAccMax);
    void adminComboDelete(String uuid);
    Map<String, Object> adminComboRecordList(String userCode, String sellerName, String startTime,
                                              String endTime, Integer page, Integer pageSize);
}
