package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.ComboService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class ComboController {

    private final ComboService comboService;

    // === 公开接口 ===

    @GetMapping("/api/combo/list")
    public Result<?> list(@RequestParam(defaultValue = "en") String lang) {
        return Result.ok(comboService.list(lang));
    }

    @GetMapping("/api/combo/{uuid}")
    public Result<?> detail(@PathVariable String uuid,
                            @RequestParam(defaultValue = "en") String lang) {
        return Result.ok(comboService.detail(uuid, lang));
    }

    // === 用户接口 ===

    @PostMapping("/api/combo/buy")
    public Result<?> buy(@RequestAttribute Long userId,
                         @RequestBody Map<String, Object> dto) {
        String comboId = (String) dto.get("comboId");
        comboService.buy(userId, comboId);
        return Result.ok();
    }

    @GetMapping("/api/combo/my")
    public Result<?> myCombos(@RequestAttribute Long userId) {
        return Result.ok(comboService.myCombos(userId));
    }

    @GetMapping("/api/combo/records")
    public Result<?> myRecords(@RequestAttribute Long userId,
                               @RequestParam(defaultValue = "1") int page,
                               @RequestParam(defaultValue = "20") int pageSize) {
        return Result.ok(comboService.myRecords(userId, page, pageSize));
    }

}
