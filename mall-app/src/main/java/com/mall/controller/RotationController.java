package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.DomainRotationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/rotation")
@RequiredArgsConstructor
public class RotationController {

    private final DomainRotationService rotationService;

    @GetMapping("/jump")
    public Result<Map<String, Object>> jump() {
        return Result.ok(rotationService.jump());
    }

    @GetMapping("/domains")
    public Result<?> listDomains() {
        return Result.ok(rotationService.listDomains());
    }

    @PostMapping("/block")
    public Result<Map<String, Object>> block(@RequestBody Map<String, String> body) {
        rotationService.blockDomain(body.get("domain"), body.getOrDefault("reason", "红名/被拦截"));
        return Result.ok(Map.of("ok", true, "domain", body.get("domain")));
    }

    @PostMapping("/unblock")
    public Result<Map<String, Object>> unblock(@RequestBody Map<String, String> body) {
        rotationService.unblockDomain(body.get("domain"));
        return Result.ok(Map.of("ok", true, "domain", body.get("domain")));
    }

    @GetMapping("/stats")
    public Result<Map<String, Object>> stats() {
        return Result.ok(rotationService.stats());
    }
}
