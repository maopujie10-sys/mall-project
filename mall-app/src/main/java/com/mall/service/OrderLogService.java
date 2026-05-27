package com.mall.service;

import com.mall.entity.MallOrderLog;
import java.util.List;

public interface OrderLogService {
    List<MallOrderLog> listByOrderId(Long userId, String orderId);
}
