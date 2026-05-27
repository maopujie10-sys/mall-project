package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.SysParamService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class SysParamController {

    private final SysParamService sysParamService;

    @GetMapping("/api/syspara/{key}")
    public Result<?> getByKey(@PathVariable String key) {
        return Result.ok(Map.of("key", key, "value", sysParamService.getString(key)));
    }

    @GetMapping("/admin/syspara/list")
    public Result<?> list() {
        return Result.ok(sysParamService.listAll());
    }

    @PostMapping("/admin/syspara")
    public Result<?> save(@RequestBody Map<String, Object> dto) {
        sysParamService.save(dto);
        return Result.ok();
    }

    @PutMapping("/admin/syspara/{id}")
    public Result<?> update(@PathVariable Long id, @RequestBody Map<String, Object> dto) {
        sysParamService.update(id, dto);
        return Result.ok();
    }

    @DeleteMapping("/admin/syspara/{id}")
    public Result<?> delete(@PathVariable Long id) {
        sysParamService.delete(id);
        return Result.ok();
    }
}
