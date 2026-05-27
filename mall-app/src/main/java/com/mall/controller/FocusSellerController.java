package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.FocusSellerService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/focus-seller")
@RequiredArgsConstructor
public class FocusSellerController {

    private final FocusSellerService focusSellerService;

    @GetMapping("/count")
    public Result<?> count(@RequestAttribute Long userId) {
        return Result.ok(focusSellerService.count(userId));
    }

    @PostMapping("/{sellerId}")
    public Result<?> follow(@RequestAttribute Long userId, @PathVariable String sellerId) {
        focusSellerService.follow(userId, sellerId);
        return Result.ok();
    }

    @DeleteMapping("/{sellerId}")
    public Result<?> unfollow(@RequestAttribute Long userId, @PathVariable String sellerId) {
        focusSellerService.unfollow(userId, sellerId);
        return Result.ok();
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") int page,
                          @RequestParam(defaultValue = "20") int pageSize) {
        return Result.ok(focusSellerService.list(userId, page, pageSize));
    }

    @GetMapping("/check/{sellerId}")
    public Result<?> isFollowed(@RequestAttribute Long userId, @PathVariable String sellerId) {
        return Result.ok(focusSellerService.isFollowed(userId, sellerId));
    }
}
