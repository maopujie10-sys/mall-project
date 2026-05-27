package com.mall.service;

import java.util.List;
import java.util.Map;

public interface SellerService {
    List<Map<String, Object>> sellerList(Map<String, Object> params);
    Map<String, Object> sellerDetail(String sellerId);
    Map<String, Object> sellerGoods(String sellerId, Integer page, Integer pageSize);
    Map<String, Object> clientVersion();
    Map<String, Object> clientVersionByPlatform(String platform, String lang);
    Map<String, Object> registerSeller(Map<String, Object> dto);
    Map<String, Object> registerSellerJs(Map<String, Object> dto);
    void updateSignPdf(Long userId, String signPdfUrl);
}
