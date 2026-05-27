package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.MallLevelService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/malllevel")
@RequiredArgsConstructor
public class MallLevelController {

    private final MallLevelService mallLevelService;

    @GetMapping("/list")
    public Result<?> list() {
        return Result.ok(mallLevelService.levelList());
    }

    @GetMapping("/{uuid}")
    public Result<?> detail(@PathVariable String uuid) {
        return Result.ok(mallLevelService.levelDetail(uuid));
    }

    @GetMapping("/config")
    public Result<?> config() {
        return Result.ok(mallLevelService.levelConfig());
    }
}
