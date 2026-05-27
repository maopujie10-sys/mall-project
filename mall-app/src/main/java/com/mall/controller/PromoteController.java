package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.PromoteService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/promote")
@RequiredArgsConstructor
public class PromoteController {

    private final PromoteService promoteService;

    @GetMapping("/my")
    public Result<?> myPromotion(@RequestAttribute Long userId) {
        return Result.ok(promoteService.myPromotion(userId));
    }

    @GetMapping("/team")
    public Result<?> teamInfo(@RequestAttribute Long userId) {
        return Result.ok(promoteService.teamInfo(userId));
    }

    @GetMapping("/car")
    public Result<?> carView(@RequestAttribute Long userId) {
        return Result.ok(promoteService.carView(userId));
    }

    @PostMapping("/car/buy")
    public Result<?> carBuy(@RequestAttribute Long userId, @RequestBody Map<String, String> data) {
        promoteService.carBuy(userId, data.get("comboId"));
        return Result.ok();
    }

    @GetMapping("/car/history")
    public Result<?> carHistory(@RequestAttribute Long userId) {
        return Result.ok(promoteService.carHistory(userId));
    }

    @PostMapping("/receive-bonus")
    public Result<?> receiveBonus(@RequestAttribute Long userId) {
        return Result.ok(promoteService.receiveBonus(userId));
    }

    @PostMapping("/receive-invite-rewards")
    public Result<?> receiveInviteRewards(@RequestAttribute Long userId) {
        return Result.ok(promoteService.receiveInviteRewards(userId));
    }
}
