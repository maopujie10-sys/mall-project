package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.CartService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/cart")
@RequiredArgsConstructor
public class CartController {

    private final CartService cartService;

    @PostMapping("/add")
    public Result<?> add(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        Long productId = Long.valueOf(dto.get("productId").toString());
        Long skuId = Long.valueOf(dto.get("skuId").toString());
        Integer quantity = Integer.parseInt(dto.get("quantity").toString());
        cartService.add(userId, productId, skuId, quantity);
        return Result.ok();
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId) {
        return Result.ok(cartService.list(userId));
    }

    @PutMapping("/{id}")
    public Result<?> update(@RequestAttribute Long userId, @PathVariable Long id,
                            @RequestBody Map<String, Integer> dto) {
        cartService.update(userId, id, dto.get("quantity"));
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<?> remove(@RequestAttribute Long userId, @PathVariable Long id) {
        cartService.remove(userId, id);
        return Result.ok();
    }
}
