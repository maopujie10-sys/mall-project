package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.CreditService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/credit")
@RequiredArgsConstructor
public class CreditController {

    private final CreditService creditService;

    @PostMapping("/apply")
    public Result<?> apply(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        creditService.apply(userId, dto);
        return Result.ok();
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId) {
        return Result.ok(creditService.list(userId));
    }

    @GetMapping("/{uuid}")
    public Result<?> detail(@RequestAttribute Long userId, @PathVariable String uuid) {
        return Result.ok(creditService.detail(userId, uuid));
    }

    @PostMapping("/{uuid}/repay")
    public Result<?> repay(@RequestAttribute Long userId, @PathVariable String uuid,
                           @RequestBody Map<String, Object> dto) {
        creditService.repay(userId, uuid, dto);
        return Result.ok();
    }
}
