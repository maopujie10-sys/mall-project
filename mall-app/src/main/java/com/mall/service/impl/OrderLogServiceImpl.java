package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mall.entity.MallOrderLog;
import com.mall.mapper.MallOrderLogMapper;
import com.mall.service.OrderLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class OrderLogServiceImpl implements OrderLogService {

    private final MallOrderLogMapper orderLogMapper;

    @Override
    public List<MallOrderLog> listByOrderId(Long userId, String orderId) {
        return orderLogMapper.selectList(
            new LambdaQueryWrapper<MallOrderLog>()
                .eq(MallOrderLog::getOrderId, orderId)
                .eq(MallOrderLog::getPartyId, String.valueOf(userId))
                .orderByAsc(MallOrderLog::getCreateTime)
        );
    }
}
