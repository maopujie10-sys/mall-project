package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.KycHighLevelService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class KycHighLevelController {

    private final KycHighLevelService kycHighLevelService;

    @GetMapping("/api/kyc-high-level")
    public Result<?> get(@RequestAttribute Long userId) {
        Map<String, Object> data = kycHighLevelService.get(userId);
        return Result.ok(data);
    }

    @PostMapping("/api/kyc-high-level/apply")
    public Result<?> apply(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        kycHighLevelService.apply(userId, dto);
        return Result.ok();
    }
}
