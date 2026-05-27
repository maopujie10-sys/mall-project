package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.KycService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class KycController {

    private final KycService kycService;

    @PostMapping("/api/kyc/submit")
    public Result<?> submit(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        kycService.submit(userId, dto);
        return Result.ok();
    }

    @GetMapping("/api/kyc/status")
    public Result<?> status(@RequestAttribute Long userId) {
        return Result.ok(kycService.status(userId));
    }

    @GetMapping("/admin/kyc/list")
    public Result<?> list(@RequestParam(defaultValue = "1") Integer pageNum,
                          @RequestParam(defaultValue = "20") Integer pageSize,
                          @RequestParam(required = false) Integer status) {
        return Result.ok(kycService.list(pageNum, pageSize, status));
    }

    @PostMapping("/admin/kyc/audit/{id}")
    public Result<?> audit(@RequestAttribute Long userId,
                           @PathVariable Long id,
                           @RequestBody Map<String, Object> dto) {
        Boolean approved = (Boolean) dto.get("approved");
        String reason = (String) dto.get("reason");
        kycService.audit(id, approved, reason, userId);
        return Result.ok();
    }
}
