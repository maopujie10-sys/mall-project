package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.BannerService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/banner")
@RequiredArgsConstructor
public class BannerController {

    private final BannerService bannerService;

    @GetMapping("/list")
    public Result<?> list(@RequestParam(defaultValue = "") String type,
                          @RequestParam(required = false) String imgType,
                          @RequestParam(defaultValue = "1") int page,
                          @RequestParam(defaultValue = "20") int pageSize) {
        return Result.ok(bannerService.list(type, imgType, null, null, page, pageSize));
    }
}
