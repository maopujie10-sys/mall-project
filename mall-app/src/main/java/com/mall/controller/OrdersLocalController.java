package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.OrderService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class OrdersLocalController {

    private final OrderService orderService;

    @PostMapping("/api/order-local/submit")
    public Result<?> submit(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        String goodsUuid = (String) dto.get("uuid");
        int num = Integer.parseInt(dto.getOrDefault("num", "1").toString());
        return Result.ok(Map.of("orderList", orderService.saveGoodsBuy(userId, goodsUuid, num)));
    }
}
