package com.mall.service;

import java.util.Map;

public interface SystemGoodsService {
    Map<String, Object> adminList(String name, String categoryId, Integer isShelf, Integer updateStatus, Integer page, Integer pageSize);

    Map<String, Object> merchantList(String keyword, Integer pageNum, Integer pageSize);
    Map<String, Object> adminDetail(String id, String lang);
    void adminSave(Map<String, Object> dto);
    void adminUpdate(Map<String, Object> dto);
    void adminDelete(String id);
    void adminUpdateShelf(String id, Integer isShelf);
    void deleteSku(String skuId);
}
