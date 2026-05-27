package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.OrderService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/order")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    @PostMapping("/create")
    public Result<?> create(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> items = (List<Map<String, Object>>) dto.get("items");
        return Result.ok(orderService.createOrder(userId, items));
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") Integer pageNum,
                          @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(orderService.list(userId, pageNum, pageSize));
    }

    @GetMapping("/{id}")
    public Result<?> detail(@RequestAttribute Long userId, @PathVariable Long id) {
        return Result.ok(orderService.detail(userId, id));
    }

    @PostMapping("/cancel/{id}")
    public Result<?> cancel(@RequestAttribute Long userId, @PathVariable Long id) {
        orderService.cancel(userId, id);
        return Result.ok();
    }

    @PostMapping("/receipt/{id}")
    public Result<?> receipt(@RequestAttribute Long userId, @PathVariable String id) {
        orderService.receipt(userId, id);
        return Result.ok();
    }

    @GetMapping("/count-status")
    public Result<?> countStatus(@RequestAttribute Long userId) {
        return Result.ok(orderService.countStatus(userId));
    }

    @PostMapping("/refund/{id}")
    public Result<?> refund(@RequestAttribute Long userId, @PathVariable Long id,
                            @RequestBody Map<String, String> body) {
        orderService.refund(userId, id, body.get("reason"));
        return Result.ok();
    }

    @PostMapping("/refund")
    public Result<?> refundApply(@RequestAttribute Long userId, @RequestBody Map<String, Object> body) {
        String orderId = (String) body.get("orderId");
        String returnReason = (String) body.get("returnReason");
        String returnDetail = (String) body.get("returnDetail");
        java.math.BigDecimal money = body.get("money") != null
            ? new java.math.BigDecimal(body.get("money").toString()) : java.math.BigDecimal.ZERO;
        orderService.refundApply(userId, orderId, returnReason, money, returnDetail);
        return Result.ok();
    }
}
