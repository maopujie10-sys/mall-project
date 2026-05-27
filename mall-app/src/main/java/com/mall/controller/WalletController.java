package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.WalletService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/wallet")
@RequiredArgsConstructor
public class WalletController {

    private final WalletService walletService;

    @GetMapping("/logs")
    public Result<?> logs(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") Integer page,
                          @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(walletService.logs(userId, page, pageSize));
    }

    @GetMapping("/balance")
    public Result<?> balanceDetail(@RequestAttribute Long userId) {
        return Result.ok(walletService.balanceDetail(userId));
    }
}
