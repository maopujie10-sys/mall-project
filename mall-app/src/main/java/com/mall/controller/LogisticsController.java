package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.LogisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/logistics")
@RequiredArgsConstructor
public class LogisticsController {

    private final LogisticsService logisticsService;

    @GetMapping("/{orderId}")
    public Result<?> info(@RequestAttribute Long userId, @PathVariable String orderId) {
        return Result.ok(logisticsService.info(userId, orderId));
    }

    @GetMapping("/{orderId}/trace")
    public Result<?> trace(@RequestAttribute Long userId, @PathVariable String orderId) {
        return Result.ok(logisticsService.trace(userId, orderId));
    }
}
