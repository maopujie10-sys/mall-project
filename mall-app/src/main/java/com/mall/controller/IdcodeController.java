package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.IdcodeService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/idcode")
@RequiredArgsConstructor
public class IdcodeController {

    private final IdcodeService idcodeService;

    @PostMapping("/send")
    public Result<?> send(@RequestBody Map<String, String> body, HttpServletRequest request) {
        String target = body.getOrDefault("target", body.get("phone"));
        String type = body.getOrDefault("type", "REGISTER");
        if (target == null || target.isEmpty()) {
            return Result.fail("手机号或邮箱不能为空");
        }
        String ip = request.getRemoteAddr();
        idcodeService.send(target, type, ip);
        return Result.ok();
    }

    @PostMapping("/verify")
    public Result<?> verify(@RequestBody Map<String, String> body) {
        String target = body.getOrDefault("target", body.get("phone"));
        String code = body.get("code");
        String type = body.getOrDefault("type", "REGISTER");
        if (target == null || target.isEmpty()) {
            return Result.fail("手机号或邮箱不能为空");
        }
        if (code == null || code.isEmpty()) {
            return Result.fail("验证码不能为空");
        }
        boolean ok = idcodeService.verify(target, code, type);
        return Result.ok(Map.of("valid", ok));
    }
}
