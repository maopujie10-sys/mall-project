package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.WithdrawService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;

@RestController
@RequestMapping("/api/withdraw")
@RequiredArgsConstructor
public class WithdrawController {

    private final WithdrawService withdrawService;

    @PostMapping("/apply")
    public Result<?> apply(@RequestAttribute Long userId, @RequestBody Map<String, String> dto) {
        return Result.ok(withdrawService.apply(userId,
            new BigDecimal(dto.get("amount")),
            dto.get("usdtAddress")));
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") Integer pageNum,
                          @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(withdrawService.list(userId, pageNum, pageSize));
    }

    @GetMapping("/fee")
    public Result<?> fee(@RequestAttribute Long userId,
                         @RequestParam(defaultValue = "USDT") String channel) {
        return Result.ok(withdrawService.getFee(userId, channel));
    }
}
