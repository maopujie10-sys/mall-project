package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.exception.BizException;
import com.mall.entity.MallOrder;
import com.mall.entity.MallOrderLog;
import com.mall.mapper.MallOrderLogMapper;
import com.mall.mapper.MallOrderMapper;
import com.mall.service.LogisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class LogisticsServiceImpl implements LogisticsService {

    private final MallOrderMapper orderMapper;
    private final MallOrderLogMapper orderLogMapper;

    @Override
    public Map<String, Object> info(Long userId, String orderId) {
        String partyId = userId.toString();
        MallOrder order = orderMapper.selectOne(
            new QueryWrapper<MallOrder>().eq("uuid", orderId).eq("party_id", partyId));
        if (order == null) throw new BizException("订单不存在");

        if (order.getLogisticsNo() == null && order.getLogisticsCompany() == null) {
            throw new BizException("该订单暂无物流信息");
        }

        Map<String, Object> map = new HashMap<>();
        map.put("orderId", order.getUuid());
        map.put("orderNo", order.getOrderNo());
        map.put("logisticsNo", order.getLogisticsNo());
        map.put("logisticsCompany", order.getLogisticsCompany());
        map.put("deliveryStatus", order.getDeliveryStatus());
        map.put("deliveryTime", order.getDeliveryTime());
        map.put("orderStatus", order.getOrderStatus());
        return map;
    }

    @Override
    public Map<String, Object> trace(Long userId, String orderId) {
        String partyId = userId.toString();
        MallOrder order = orderMapper.selectOne(
            new QueryWrapper<MallOrder>().eq("uuid", orderId).eq("party_id", partyId));
        if (order == null) throw new BizException("订单不存在");

        List<MallOrderLog> logs = orderLogMapper.selectList(
            new QueryWrapper<MallOrderLog>()
                .eq("order_id", orderId)
                .orderByAsc("create_time"));

        List<Map<String, Object>> traceList = new ArrayList<>();
        for (MallOrderLog log : logs) {
            Map<String, Object> item = new HashMap<>();
            item.put("uuid", log.getUuid());
            item.put("state", log.getState());
            item.put("category", log.getCategory());
            item.put("log", log.getLog());
            item.put("username", log.getUsername());
            item.put("createTime", log.getCreateTime());
            traceList.add(item);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("orderId", order.getUuid());
        result.put("orderNo", order.getOrderNo());
        result.put("logisticsNo", order.getLogisticsNo());
        result.put("logisticsCompany", order.getLogisticsCompany());
        result.put("deliveryStatus", order.getDeliveryStatus());
        result.put("traces", traceList);
        return result;
    }
}
