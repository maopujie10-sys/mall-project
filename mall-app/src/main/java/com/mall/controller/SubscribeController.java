package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.SubscribeService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/subscribe")
@RequiredArgsConstructor
public class SubscribeController {

    private final SubscribeService subscribeService;

    @PostMapping
    public Result<?> subscribe(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        subscribeService.subscribe(userId, dto);
        return Result.ok();
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId) {
        return Result.ok(subscribeService.list(userId));
    }

    @PutMapping("/{id}")
    public Result<?> update(@RequestAttribute Long userId,
                            @PathVariable Long id,
                            @RequestBody Map<String, Object> dto) {
        subscribeService.update(userId, id, dto);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<?> delete(@RequestAttribute Long userId, @PathVariable Long id) {
        subscribeService.delete(userId, id);
        return Result.ok();
    }
}
