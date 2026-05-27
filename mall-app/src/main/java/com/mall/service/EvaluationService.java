package com.mall.service;

import java.util.List;
import java.util.Map;

public interface EvaluationService {
    List<Map<String, Object>> listByProduct(String sellerGoodsId, int page, int pageSize, Integer evaluationType);
    Map<String, Object> countByType(String sellerGoodsId);
    List<Map<String, Object>> listByUser(Long userId, int page, int pageSize);
    List<Map<String, Object>> listBySeller(String sellerId, int page, int pageSize);
    Map<String, Object> detail(String uuid);
    void create(Long userId, Map<String, Object> dto);
    void delete(Long userId, String uuid);

    // === Admin ===
    Map<String, Object> adminList(String keyword, Integer status, Integer page, Integer pageSize);
    void adminUpdateStatus(String uuid, Integer status);
    void adminDelete(String uuid);

    // === System Comment (对应旧AdminSystemGoodsController/AdminSystemCommentController) ===
    Map<String, Object> systemCommentList(String systemGoodsId, Integer status, Integer page, Integer pageSize);
    void systemCommentSave(Map<String, Object> dto);
    void systemCommentUpdateStatus(String id, Integer status);
    void systemCommentDelete(String id);
}
