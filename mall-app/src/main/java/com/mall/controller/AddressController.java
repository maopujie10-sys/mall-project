package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.AddressService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/address")
@RequiredArgsConstructor
public class AddressController {

    private final AddressService addressService;

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId) {
        return Result.ok(addressService.list(userId));
    }

    @GetMapping("/{uuid}")
    public Result<?> detail(@RequestAttribute Long userId, @PathVariable String uuid) {
        return Result.ok(addressService.detail(userId, uuid));
    }

    @PostMapping
    public Result<?> add(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        addressService.add(userId, dto);
        return Result.ok();
    }

    @PutMapping("/{uuid}")
    public Result<?> update(@RequestAttribute Long userId, @PathVariable String uuid,
                            @RequestBody Map<String, Object> dto) {
        addressService.update(userId, uuid, dto);
        return Result.ok();
    }

    @DeleteMapping("/{uuid}")
    public Result<?> delete(@RequestAttribute Long userId, @PathVariable String uuid) {
        addressService.delete(userId, uuid);
        return Result.ok();
    }

    @PutMapping("/{uuid}/default")
    public Result<?> setDefault(@RequestAttribute Long userId, @PathVariable String uuid) {
        addressService.setDefault(userId, uuid);
        return Result.ok();
    }
}
