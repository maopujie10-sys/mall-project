package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.SellerService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
public class SellerVersionController {

    private final SellerService sellerService;

    /** 商户客户端版本信息 */
    @PostMapping("/seller/version/client")
    public Result<?> client(@RequestBody Map<String, String> dto) {
        String platform = dto.getOrDefault("plantform", "0");
        if (!platform.equals("1") && !platform.equals("2")) {
            return Result.ok(Map.of("plantform", "0"));
        }
        String lang = dto.getOrDefault("lang", "en");
        return Result.ok(sellerService.clientVersionByPlatform(platform, lang));
    }

    /** 店铺注册 */
    @PostMapping("/seller/version/register")
    public Result<?> register(@RequestBody Map<String, Object> dto) {
        return Result.ok(sellerService.registerSeller(dto));
    }

    /** JustShop/Argos2 商家入驻 */
    @PostMapping("/seller/version/register-js")
    public Result<?> registerJs(@RequestBody Map<String, Object> dto) {
        return Result.ok(sellerService.registerSellerJs(dto));
    }

    /** 更新店铺签名 */
    @PostMapping("/seller/version/update-sign-pdf")
    public Result<?> updateSignPdf(@RequestAttribute Long userId, @RequestBody Map<String, String> dto) {
        sellerService.updateSignPdf(userId, dto.get("signPdfUrl"));
        return Result.ok("success");
    }
}
