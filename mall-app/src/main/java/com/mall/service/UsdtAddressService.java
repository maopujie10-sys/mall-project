package com.mall.service;

import com.mall.entity.UsdtAddress;
import java.util.List;

public interface UsdtAddressService {
    List<UsdtAddress> listByUser(Long userId);
    UsdtAddress add(Long userId, String network, String address, String label);
    void delete(Long userId, Long id);
    void setActive(Long userId, Long id);
}
