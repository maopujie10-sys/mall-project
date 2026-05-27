package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.SellerService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/seller")
@RequiredArgsConstructor
public class SellerController {

    private final SellerService sellerService;

    @GetMapping("/list")
    public Result<?> list(@RequestParam(required = false) Map<String, Object> params) {
        return Result.ok(sellerService.sellerList(params));
    }

    @GetMapping("/{sellerId}")
    public Result<?> detail(@PathVariable String sellerId) {
        return Result.ok(sellerService.sellerDetail(sellerId));
    }

    @GetMapping("/{sellerId}/goods")
    public Result<?> goods(@PathVariable String sellerId,
                           @RequestParam(defaultValue = "1") Integer page,
                           @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(sellerService.sellerGoods(sellerId, page, pageSize));
    }

    @GetMapping("/client/latest")
    public Result<?> clientVersion() {
        return Result.ok(sellerService.clientVersion());
    }
}
