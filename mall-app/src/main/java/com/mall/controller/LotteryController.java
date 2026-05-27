package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.LotteryService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/promote/lottery")
@RequiredArgsConstructor
public class LotteryController {

    private final LotteryService lotteryService;

    @GetMapping("/current")
    public Result<?> getCurrentActivity(@RequestParam(required = false, defaultValue = "en") String lang) {
        return Result.ok(lotteryService.getCurrentActivity(lang));
    }

    @GetMapping
    public Result<?> getActivityDetail(@RequestParam String activityId,
                                       @RequestAttribute Long userId,
                                       @RequestParam(required = false, defaultValue = "en") String lang) {
        return Result.ok(lotteryService.getActivityDetail(activityId, userId, lang));
    }

    @GetMapping("/points")
    public Result<?> getPoints(@RequestParam String activityId,
                               @RequestAttribute Long userId) {
        return Result.ok(lotteryService.getPoints(activityId, userId));
    }

    @PostMapping("/points")
    public Result<?> getCountPoints(@RequestParam String activityId,
                                    @RequestAttribute Long userId) {
        return Result.ok(lotteryService.getCountPoints(activityId, userId));
    }

    @PostMapping("/draw")
    public Result<?> draw(@RequestParam String activityId,
                          @RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") int drawTimes,
                          @RequestParam(required = false, defaultValue = "en") String lang) {
        return Result.ok(lotteryService.draw(activityId, userId, drawTimes, lang));
    }

    @GetMapping("/prizes")
    public Result<?> countPrize(@RequestParam String activityId,
                                @RequestAttribute Long userId) {
        return Result.ok(lotteryService.countPrize(activityId, userId));
    }

    @PostMapping("/receive")
    public Result<?> receivePrize(@RequestParam String activityId,
                                  @RequestAttribute Long userId,
                                  @RequestParam int prizeType) {
        return Result.ok(lotteryService.receivePrize(activityId, userId, prizeType));
    }

    @GetMapping("/my-prizes")
    public Result<?> pageMyPrizes(@RequestParam String activityId,
                                  @RequestAttribute Long userId,
                                  @RequestParam(defaultValue = "1") int page,
                                  @RequestParam(defaultValue = "10") int size) {
        return Result.ok(lotteryService.pageMyPrizes(activityId, userId, page, size));
    }

    @GetMapping("/activity-prize-list")
    public Result<?> listActivityPrize(@RequestParam String activityId,
                                       @RequestAttribute Long userId) {
        return Result.ok(lotteryService.listActivityPrize(activityId));
    }
}
