package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.GeetestService;
import com.mall.service.SysParamService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/geetest")
@RequiredArgsConstructor
public class GeetestController {

    private static final Logger log = LoggerFactory.getLogger(GeetestController.class);

    private final GeetestService geetestService;
    private final SysParamService sysParamService;

    @GetMapping("/challenge")
    public Result<?> getChallenge() {
        try {
            String geetestId = sysParamService.getString("geetest_id");
            String geetestKey = sysParamService.getString("geetest_key");
            String newFailback = sysParamService.getString("geetest_new_failback");

            if (isEmpty(geetestId) || isEmpty(geetestKey) || isEmpty(newFailback)) {
                return Result.fail("极验系统参数未配置");
            }

            Map<String, String> param = new HashMap<>();
            param.put("user_id", "test");
            param.put("geetest_id", geetestId);
            param.put("geetest_key", geetestKey);
            param.put("new_failback", newFailback);

            Map<String, String> retMap = geetestService.preProcess(param);
            if (retMap != null) {
                retMap.put("user_id", param.get("user_id"));
                retMap.put("gt_server_status", retMap.get("success"));
            }

            return Result.ok(retMap);
        } catch (Exception e) {
            log.error("Geetest challenge error", e);
            return Result.fail("获取验证码失败");
        }
    }

    @PostMapping("/verify")
    public Result<?> verify(@RequestBody Map<String, String> body) {
        String challenge = body.get("geetest_challenge");
        String validate = body.get("geetest_validate");
        String seccode = body.get("geetest_seccode");
        String gtServerStatus = body.get("gt_server_status");

        try {
            String geetestId = sysParamService.getString("geetest_id");
            String geetestKey = sysParamService.getString("geetest_key");
            String newFailback = sysParamService.getString("geetest_new_failback");

            if (isEmpty(geetestId) || isEmpty(geetestKey) || isEmpty(newFailback)) {
                return Result.fail("极验系统参数未配置");
            }

            Map<String, String> param = new HashMap<>();
            param.put("user_id", "test");
            param.put("challenge", challenge);
            param.put("validate", validate);
            param.put("seccode", seccode);
            param.put("geetest_id", geetestId);
            param.put("geetest_key", geetestKey);
            param.put("new_failback", newFailback);

            int gtResult;
            if ("1".equals(gtServerStatus)) {
                gtResult = geetestService.enhencedValidateRequest(param);
            } else {
                gtResult = geetestService.failbackValidateRequest(param);
            }

            Map<String, String> retMap = new HashMap<>();
            retMap.put("status", gtResult == 1 ? "success" : "fail");
            retMap.put("version", geetestService.getVersionInfo());

            return Result.ok(retMap);
        } catch (Exception e) {
            log.error("Geetest verify error", e);
            return Result.fail("验证失败");
        }
    }

    private boolean isEmpty(String s) {
        return s == null || s.trim().isEmpty();
    }
}
