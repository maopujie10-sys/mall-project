package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.RechargeService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;

@RestController
@RequestMapping("/api/recharge")
@RequiredArgsConstructor
public class RechargeController {

    private final RechargeService rechargeService;

    @PostMapping("/apply")
    public Result<?> apply(@RequestAttribute Long userId, @RequestBody Map<String, String> dto) {
        return Result.ok(rechargeService.apply(userId,
            new BigDecimal(dto.get("amount")),
            dto.get("usdtAddress"),
            dto.get("txHash"),
            dto.get("screenshot")));
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") Integer pageNum,
                          @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(rechargeService.list(userId, pageNum, pageSize));
    }
}
