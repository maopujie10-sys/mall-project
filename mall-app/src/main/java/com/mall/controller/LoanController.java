package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.LoanService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/loan")
@RequiredArgsConstructor
public class LoanController {

    private final LoanService loanService;

    @PostMapping("/apply")
    public Result<?> apply(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        loanService.apply(userId, dto);
        return Result.ok();
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(required = false) Integer page,
                          @RequestParam(required = false) Integer pageSize) {
        return Result.ok(loanService.list(userId, page, pageSize));
    }

    @GetMapping("/{uuid}")
    public Result<?> detail(@RequestAttribute Long userId, @PathVariable String uuid) {
        return Result.ok(loanService.detail(userId, uuid));
    }

    @PostMapping("/{uuid}/repay")
    public Result<?> repay(@RequestAttribute Long userId, @PathVariable String uuid,
                           @RequestBody Map<String, Object> dto) {
        loanService.repay(userId, uuid, dto);
        return Result.ok();
    }

    @GetMapping("/config")
    public Result<?> config() {
        return Result.ok(loanService.config());
    }

    @GetMapping("/admin/list")
    public Result<?> adminList(@RequestAttribute Long userId,
                               @RequestParam(required = false) String keyword,
                               @RequestParam(required = false) Integer status,
                               @RequestParam(required = false) Integer page,
                               @RequestParam(required = false) Integer pageSize) {
        return Result.ok(loanService.adminList(keyword, status, page, pageSize));
    }

    @PostMapping("/admin/audit")
    public Result<?> audit(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        loanService.audit(userId, dto.get("uuid").toString(), dto);
        return Result.ok();
    }

    @PostMapping("/admin/config")
    public Result<?> saveConfig(@RequestBody Map<String, Object> dto) {
        loanService.saveConfig(dto);
        return Result.ok();
    }

    @GetMapping("/admin/configs")
    public Result<?> configList() {
        return Result.ok(loanService.configList());
    }
}
