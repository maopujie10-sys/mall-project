package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.EvaluationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/evaluation")
@RequiredArgsConstructor
public class EvaluationController {

    private final EvaluationService evaluationService;

    @GetMapping("/product/{sellerGoodsId}")
    public Result<?> listByProduct(@PathVariable String sellerGoodsId,
                                   @RequestParam(defaultValue = "1") int page,
                                   @RequestParam(defaultValue = "20") int pageSize,
                                   @RequestParam(required = false) Integer evaluationType) {
        return Result.ok(evaluationService.listByProduct(sellerGoodsId, page, pageSize, evaluationType));
    }

    @GetMapping("/product/{sellerGoodsId}/counts")
    public Result<?> countByType(@PathVariable String sellerGoodsId) {
        return Result.ok(evaluationService.countByType(sellerGoodsId));
    }

    @GetMapping("/seller/{sellerId}")
    public Result<?> listBySeller(@PathVariable String sellerId,
                                  @RequestParam(defaultValue = "1") int page,
                                  @RequestParam(defaultValue = "20") int pageSize) {
        return Result.ok(evaluationService.listBySeller(sellerId, page, pageSize));
    }

    @GetMapping("/my")
    public Result<?> listByUser(@RequestAttribute Long userId,
                                @RequestParam(defaultValue = "1") int page,
                                @RequestParam(defaultValue = "20") int pageSize) {
        return Result.ok(evaluationService.listByUser(userId, page, pageSize));
    }

    @GetMapping("/{uuid}")
    public Result<?> detail(@PathVariable String uuid) {
        return Result.ok(evaluationService.detail(uuid));
    }

    @PostMapping
    public Result<?> create(@RequestAttribute Long userId,
                            @RequestBody Map<String, Object> dto) {
        evaluationService.create(userId, dto);
        return Result.ok();
    }

    @DeleteMapping("/{uuid}")
    public Result<?> delete(@RequestAttribute Long userId, @PathVariable String uuid) {
        evaluationService.delete(userId, uuid);
        return Result.ok();
    }
}
