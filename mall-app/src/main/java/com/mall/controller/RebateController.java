package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.RebateService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/rebate")
@RequiredArgsConstructor
public class RebateController {

    private final RebateService rebateService;

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") Integer page,
                          @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(rebateService.list(userId, page, pageSize));
    }

    @GetMapping("/{uuid}")
    public Result<?> detail(@RequestAttribute Long userId, @PathVariable String uuid) {
        return Result.ok(rebateService.detail(userId, uuid));
    }

    @GetMapping("/stats")
    public Result<?> stats(@RequestAttribute Long userId) {
        return Result.ok(rebateService.stats(userId));
    }
}
