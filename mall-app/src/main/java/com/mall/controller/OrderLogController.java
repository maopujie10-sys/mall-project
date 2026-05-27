package com.mall.controller;

import com.mall.common.Result;
import com.mall.entity.MallOrderLog;
import com.mall.service.OrderLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/order-log")
@RequiredArgsConstructor
public class OrderLogController {

    private final OrderLogService orderLogService;

    @GetMapping("/{orderId}")
    public Result<List<MallOrderLog>> listByOrderId(@RequestAttribute Long userId, @PathVariable String orderId) {
        return Result.ok(orderLogService.listByOrderId(userId, orderId));
    }
}
