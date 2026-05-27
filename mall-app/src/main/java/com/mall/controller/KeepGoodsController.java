package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.KeepGoodsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/keep-goods")
@RequiredArgsConstructor
public class KeepGoodsController {

    private final KeepGoodsService keepGoodsService;

    @GetMapping("/count")
    public Result<?> count(@RequestAttribute Long userId) {
        return Result.ok(keepGoodsService.count(userId));
    }

    @PostMapping("/{sellerGoodsId}")
    public Result<?> add(@RequestAttribute Long userId, @PathVariable String sellerGoodsId) {
        keepGoodsService.add(userId, sellerGoodsId);
        return Result.ok();
    }

    @DeleteMapping("/{sellerGoodsId}")
    public Result<?> remove(@RequestAttribute Long userId, @PathVariable String sellerGoodsId) {
        keepGoodsService.remove(userId, sellerGoodsId);
        return Result.ok();
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") int page,
                          @RequestParam(defaultValue = "20") int pageSize) {
        return Result.ok(keepGoodsService.list(userId, page, pageSize));
    }

    @GetMapping("/check/{sellerGoodsId}")
    public Result<?> isKept(@RequestAttribute Long userId, @PathVariable String sellerGoodsId) {
        return Result.ok(keepGoodsService.isKept(userId, sellerGoodsId));
    }
}
