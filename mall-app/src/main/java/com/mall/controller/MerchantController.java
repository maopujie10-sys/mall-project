package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.MerchantService;
import com.mall.service.PromoteService;
import com.mall.service.UsdtAddressService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/merchant")
@RequiredArgsConstructor
public class MerchantController {

    private final MerchantService merchantService;
    private final UsdtAddressService usdtAddressService;
    private final PromoteService promoteService;

    // ==================== Auth ====================

    @PostMapping("/login")
    public Result<?> login(@RequestBody Map<String, String> dto) {
        return Result.ok(merchantService.loginByUsername(dto.get("username"), dto.get("password")));
    }

    @PutMapping("/password")
    public Result<?> changePassword(@RequestAttribute Long userId, @RequestBody Map<String, String> dto) {
        merchantService.changePassword(userId, dto.get("oldPassword"), dto.get("newPassword"));
        return Result.ok();
    }

    @PostMapping("/reset-password/send-code")
    public Result<?> resetPasswordSendCode(@RequestBody Map<String, String> body,
                                           HttpServletRequest request) {
        String phone = body.get("phone");
        if (phone == null || phone.isBlank()) return Result.fail("手机号不能为空");
        merchantService.resetPasswordSendCode(phone, request.getRemoteAddr());
        return Result.ok();
    }

    @PostMapping("/reset-password")
    public Result<?> resetPassword(@RequestBody Map<String, String> body) {
        String phone = body.get("phone");
        String code = body.get("code");
        String newPassword = body.get("newPassword");
        if (phone == null || phone.isBlank()) return Result.fail("手机号不能为空");
        if (code == null || code.isBlank()) return Result.fail("验证码不能为空");
        if (newPassword == null || newPassword.isEmpty()) return Result.fail("新密码不能为空");
        merchantService.resetPassword(phone, code, newPassword);
        return Result.ok();
    }

    // ==================== Dashboard ====================

    @GetMapping("/dashboard")
    public Result<?> dashboard(@RequestAttribute Long userId) {
        return Result.ok(merchantService.dashboard(userId));
    }

    // ==================== Info & Store ====================

    @GetMapping("/info")
    public Result<?> info(@RequestAttribute Long userId) {
        return Result.ok(merchantService.getInfo(userId));
    }

    @PutMapping("/shop")
    public Result<?> updateShop(@RequestAttribute Long userId, @RequestBody Map<String, Object> data) {
        merchantService.updateShopInfo(userId, data);
        return Result.ok();
    }

    @PostMapping("/account/delete")
    public Result<?> deleteAccount(@RequestAttribute Long userId, @RequestBody Map<String, String> data) {
        merchantService.deleteAccount(userId, data.get("password"), data.get("reason"));
        return Result.ok();
    }

    // ==================== Product CRUD ====================

    @GetMapping("/product/list")
    public Result<?> productList(@RequestAttribute Long userId,
                                  @RequestParam(defaultValue = "1") Integer pageNum,
                                  @RequestParam(defaultValue = "10") Integer pageSize,
                                  @RequestParam(required = false) String keyword,
                                  @RequestParam(required = false) Integer status) {
        return Result.ok(merchantService.productList(userId, pageNum, pageSize, keyword, status));
    }

    @GetMapping("/product/{id}")
    public Result<?> productDetail(@RequestAttribute Long userId, @PathVariable Long id) {
        return Result.ok(merchantService.productDetail(userId, id));
    }

    @PostMapping("/product")
    public Result<?> productAdd(@RequestAttribute Long userId, @RequestBody Map<String, Object> data) {
        merchantService.productAdd(userId, data);
        return Result.ok();
    }

    @PutMapping("/product/{id}")
    public Result<?> productUpdate(@RequestAttribute Long userId, @PathVariable Long id,
                                    @RequestBody Map<String, Object> data) {
        merchantService.productUpdate(userId, id, data);
        return Result.ok();
    }

    @DeleteMapping("/product/{id}")
    public Result<?> productDelete(@RequestAttribute Long userId, @PathVariable Long id) {
        merchantService.productDelete(userId, id);
        return Result.ok();
    }

    @PutMapping("/product/{id}/status")
    public Result<?> productUpdateStatus(@RequestAttribute Long userId, @PathVariable Long id,
                                          @RequestBody Map<String, Integer> data) {
        merchantService.productUpdateStatus(userId, id, data.get("status"));
        return Result.ok();
    }

    // ==================== Orders ====================

    @GetMapping("/order/list")
    public Result<?> orderList(@RequestAttribute Long userId,
                                @RequestParam(defaultValue = "1") Integer pageNum,
                                @RequestParam(defaultValue = "10") Integer pageSize,
                                @RequestParam(required = false) Integer status) {
        return Result.ok(merchantService.orderList(userId, pageNum, pageSize, status));
    }

    @GetMapping("/order/{id}")
    public Result<?> orderDetail(@RequestAttribute Long userId, @PathVariable String id) {
        return Result.ok(merchantService.orderDetail(userId, id));
    }

    @PostMapping("/order/ship/{id}")
    public Result<?> ship(@RequestAttribute Long userId, @PathVariable String id,
                          @RequestBody Map<String, String> dto) {
        merchantService.shipOrder(userId, id, dto.get("company"), dto.get("trackingNo"));
        return Result.ok();
    }

    // ==================== Reviews ====================

    @GetMapping("/review/list")
    public Result<?> reviewList(@RequestAttribute Long userId,
                                 @RequestParam(defaultValue = "1") Integer pageNum,
                                 @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(merchantService.reviewList(userId, pageNum, pageSize));
    }

    // ==================== Refund ====================

    @GetMapping("/refund/list")
    public Result<?> refundList(@RequestAttribute Long userId,
                                 @RequestParam(defaultValue = "1") Integer pageNum,
                                 @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(merchantService.refundList(userId, pageNum, pageSize));
    }

    @PostMapping("/refund/{id}/process")
    public Result<?> refundProcess(@RequestAttribute Long userId, @PathVariable String id,
                                    @RequestBody Map<String, Object> dto) {
        merchantService.refundProcess(userId, id, Boolean.parseBoolean(dto.get("approved").toString()));
        return Result.ok();
    }

    // ==================== SKU Management ====================

    @GetMapping("/product/{productId}/skus")
    public Result<?> skuList(@RequestAttribute Long userId, @PathVariable String productId) {
        return Result.ok(merchantService.skuList(userId, productId));
    }

    @PostMapping("/product/{productId}/sku")
    public Result<?> skuAdd(@RequestAttribute Long userId, @PathVariable String productId,
                             @RequestBody Map<String, Object> dto) {
        merchantService.skuAdd(userId, productId, dto);
        return Result.ok();
    }

    @PutMapping("/product/{productId}/sku/{skuId}")
    public Result<?> skuUpdate(@RequestAttribute Long userId, @PathVariable String productId,
                                @PathVariable String skuId, @RequestBody Map<String, Object> dto) {
        merchantService.skuUpdate(userId, skuId, dto);
        return Result.ok();
    }

    @DeleteMapping("/product/{productId}/sku/{skuId}")
    public Result<?> skuDelete(@RequestAttribute Long userId, @PathVariable String productId,
                                @PathVariable String skuId) {
        merchantService.skuDelete(userId, skuId);
        return Result.ok();
    }

    // ==================== Wallet ====================

    @GetMapping("/wallet")
    public Result<?> walletInfo(@RequestAttribute Long userId) {
        return Result.ok(merchantService.walletInfo(userId));
    }

    @GetMapping("/recharge/list")
    public Result<?> rechargeList(@RequestAttribute Long userId,
                                   @RequestParam(defaultValue = "1") Integer pageNum,
                                   @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(merchantService.rechargeList(userId, pageNum, pageSize));
    }

    @GetMapping("/withdraw/list")
    public Result<?> withdrawList(@RequestAttribute Long userId,
                                   @RequestParam(defaultValue = "1") Integer pageNum,
                                   @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(merchantService.withdrawList(userId, pageNum, pageSize));
    }

    @PostMapping("/recharge/apply")
    public Result<?> rechargeApply(@RequestAttribute Long userId, @RequestBody Map<String, Object> data) {
        merchantService.rechargeApply(userId, data);
        return Result.ok();
    }

    @PostMapping("/withdraw/apply")
    public Result<?> withdrawApply(@RequestAttribute Long userId, @RequestBody Map<String, Object> data) {
        merchantService.withdrawApply(userId, data);
        return Result.ok();
    }

    // ==================== Balance Log ====================

    @GetMapping("/balance/log")
    public Result<?> balanceLog(@RequestAttribute Long userId,
                                 @RequestParam(defaultValue = "1") Integer pageNum,
                                 @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(merchantService.balanceLogList(userId, pageNum, pageSize));
    }

    // ==================== Financial Report ====================

    @GetMapping("/finance/report")
    public Result<?> financeReport(@RequestAttribute Long userId,
                                    @RequestParam(required = false) String startDate,
                                    @RequestParam(required = false) String endDate) {
        return Result.ok(merchantService.financeReport(userId, startDate, endDate));
    }

    // ==================== Customer Service ====================

    @GetMapping("/chat/list")
    public Result<?> chatList(@RequestAttribute Long userId,
                               @RequestParam(defaultValue = "1") Integer pageNum,
                               @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(merchantService.chatList(userId, pageNum, pageSize));
    }

    @GetMapping("/chat/conversation/{fromUserId}")
    public Result<?> chatConversation(@RequestAttribute Long userId, @PathVariable Long fromUserId) {
        return Result.ok(merchantService.chatConversation(userId, fromUserId));
    }

    @PostMapping("/chat/reply/{toUserId}")
    public Result<?> chatReply(@RequestAttribute Long userId, @PathVariable Long toUserId,
                                @RequestBody Map<String, String> dto) {
        merchantService.chatReply(userId, toUserId, dto.get("content"));
        return Result.ok();
    }

    // ==================== USDT Address ====================

    @GetMapping("/usdt-address/list")
    public Result<?> usdtAddressList(@RequestAttribute Long userId) {
        return Result.ok(usdtAddressService.listByUser(userId));
    }

    @PostMapping("/usdt-address")
    public Result<?> usdtAddressAdd(@RequestAttribute Long userId, @RequestBody Map<String, String> dto) {
        return Result.ok(usdtAddressService.add(userId, dto.get("network"), dto.get("address"), dto.get("label")));
    }

    @DeleteMapping("/usdt-address/{id}")
    public Result<?> usdtAddressDelete(@RequestAttribute Long userId, @PathVariable Long id) {
        usdtAddressService.delete(userId, id);
        return Result.ok();
    }

    @PutMapping("/usdt-address/{id}/active")
    public Result<?> usdtAddressSetActive(@RequestAttribute Long userId, @PathVariable Long id) {
        usdtAddressService.setActive(userId, id);
        return Result.ok();
    }

    // ==================== Settle (Merchant Apply, public) ====================

    @PostMapping("/settle")
    public Result<?> settle(@RequestBody Map<String, Object> data) {
        merchantService.settle(data);
        return Result.ok();
    }

    @GetMapping("/settle/status")
    public Result<?> settleStatus(@RequestParam String phone) {
        return Result.ok(merchantService.settleStatus(phone));
    }

    // ==================== Library (System Goods) ====================

    @GetMapping("/library/list")
    public Result<?> libraryList(@RequestAttribute Long userId,
                                 @RequestParam(required = false) String keyword,
                                 @RequestParam(defaultValue = "1") Integer pageNum,
                                 @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(merchantService.libraryList(keyword, pageNum, pageSize));
    }

    @PostMapping("/library/purchase")
    public Result<?> libraryPurchase(@RequestAttribute Long userId,
                                      @RequestBody Map<String, String> data) {
        merchantService.libraryPurchase(userId, data.get("systemGoodsId"));
        return Result.ok();
    }

    // ==================== Car / Promote ====================

    @GetMapping("/promote/car/view")
    public Result<?> carView(@RequestAttribute Long userId) {
        return Result.ok(promoteService.carView(userId));
    }

    @PostMapping("/promote/car/buy")
    public Result<?> carBuy(@RequestAttribute Long userId,
                            @RequestBody Map<String, Object> data) {
        Integer days = data.get("days") instanceof Integer ?
            (Integer) data.get("days") : Integer.valueOf(data.get("days").toString());
        merchantService.carBuy(userId, days);
        return Result.ok();
    }

    @GetMapping("/promote/car/history")
    public Result<?> carHistory(@RequestAttribute Long userId) {
        return Result.ok(merchantService.carHistory(userId));
    }
}
