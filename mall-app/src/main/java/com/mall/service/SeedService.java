package com.mall.service;

import java.util.Map;

public interface SeedService {
    Map<String, Object> generateProducts(int count);
    Map<String, Object> generateOrders(int count);
    Map<String, Object> generateCart(int count);
    Map<String, Object> generateAddresses(int count);
    Map<String, Object> generateMerchants(int count);
    Map<String, Object> generateComments(int count);
    Map<String, Object> generateUsers(int count);
    Map<String, Object> clearAll();
}
