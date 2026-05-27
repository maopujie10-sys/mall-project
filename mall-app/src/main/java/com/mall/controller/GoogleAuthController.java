package com.mall.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.Result;
import com.mall.entity.User;
import com.mall.mapper.UserMapper;
import com.mall.service.GoogleAuthService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/google-auth")
@RequiredArgsConstructor
public class GoogleAuthController {

    private static final Logger log = LoggerFactory.getLogger(GoogleAuthController.class);

    private final GoogleAuthService googleAuthService;
    private final UserMapper userMapper;

    /** 获取密钥及二维码（未绑定时返回），已绑定只返回绑定状态 */
    @GetMapping("/secret")
    public Result<?> getSecret(@RequestAttribute Long userId) {
        try {
            User user = userMapper.selectById(userId);
            if (user == null) {
                return Result.fail("用户不存在");
            }

            Map<String, Object> data = new HashMap<>();
            if (isBlank(user.getGoogleAuthSecret())) {
                Map<String, String> result = googleAuthService.generateSecret(user.getEmail());
                data.put("google_auth_secret", result.get("secret"));
                data.put("google_auth_url", result.get("qrUrl"));
                data.put("google_auth_bind", false);
            } else {
                data.put("google_auth_bind", true);
            }

            return Result.ok(data);
        } catch (Exception e) {
            log.error("GoogleAuth getSecret error", e);
            return Result.fail("获取谷歌验证器信息失败");
        }
    }

    /** 绑定谷歌验证器：提交 secret + 当前 TOTP 码 */
    @PostMapping("/bind")
    public Result<?> bind(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String secret = body.get("secret");
        String code = body.get("code");

        if (isBlank(secret)) {
            return Result.fail("secret不能为空");
        }
        if (isBlank(code)) {
            return Result.fail("验证码不能为空");
        }

        try {
            int codeInt;
            try {
                codeInt = Integer.parseInt(code);
            } catch (NumberFormatException e) {
                return Result.fail("验证码格式错误");
            }

            if (!googleAuthService.verifyCode(secret, codeInt)) {
                return Result.fail("谷歌验证码错误");
            }

            User user = userMapper.selectById(userId);
            user.setGoogleAuthSecret(secret);
            userMapper.updateById(user);

            Map<String, Object> data = new HashMap<>();
            data.put("google_auth_bind", true);
            return Result.ok(data);
        } catch (Exception e) {
            log.error("GoogleAuth bind error", e);
            return Result.fail("绑定失败");
        }
    }

    /** 验证谷歌验证码（提现/敏感操作时调用） */
    @PostMapping("/verify")
    public Result<?> verify(@RequestAttribute Long userId, @RequestBody Map<String, String> body) {
        String code = body.get("code");

        if (isBlank(code)) {
            return Result.fail("验证码不能为空");
        }

        try {
            User user = userMapper.selectById(userId);
            if (isBlank(user.getGoogleAuthSecret())) {
                return Result.fail("请先绑定谷歌验证器");
            }

            int codeInt;
            try {
                codeInt = Integer.parseInt(code);
            } catch (NumberFormatException e) {
                return Result.fail("验证码格式错误");
            }

            boolean checkResult = googleAuthService.verifyCode(user.getGoogleAuthSecret(), codeInt);
            Map<String, Object> data = new HashMap<>();
            data.put("check_result", checkResult);
            return Result.ok(data);
        } catch (Exception e) {
            log.error("GoogleAuth verify error", e);
            return Result.fail("验证失败");
        }
    }

    private boolean isBlank(String s) {
        return s == null || s.isBlank();
    }
}
