package com.mall.controller;

import com.mall.common.Result;
import com.mall.common.exception.BizException;
import com.mall.service.ComboService;
import com.mall.service.PromoteService;
import com.mall.service.SysParamService;
import com.mall.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequiredArgsConstructor
public class SellerPromotionalController {

    private final ComboService comboService;
    private final PromoteService promoteService;
    private final SysParamService sysParamService;
    private final UserService userService;

    /** 直通车套餐列表 */
    @GetMapping("/seller/promotional/view")
    public Result<?> view(@RequestParam(defaultValue = "en") String lang) {
        return Result.ok(Map.of("line", comboService.list(lang)));
    }

    /** 购买直通车套餐 (需资金密码) */
    @PostMapping("/seller/promotional/buy")
    public Result<?> buy(@RequestAttribute Long userId, @RequestBody Map<String, String> dto) {
        String comboId = dto.get("id");
        String safeword = dto.get("safeword");

        if (comboId == null || comboId.length() < 5 || comboId.length() > 50)
            return Result.fail("订单不存在");
        if (safeword == null || safeword.isEmpty())
            return Result.fail("资金密码不能为空");
        if (safeword.length() < 6 || safeword.length() > 12)
            return Result.fail("资金密码必须6-12位");

        if (!userService.verifySafeword(userId, safeword))
            return Result.fail("资金密码错误");

        comboService.buy(userId, comboId);
        return Result.ok();
    }

    /** 直通车购买记录 */
    @GetMapping("/seller/promotional/list-buy")
    public Result<?> listBuy(@RequestAttribute Long userId,
                             @RequestParam(defaultValue = "1") int page,
                             @RequestParam(defaultValue = "20") int pageSize) {
        return Result.ok(comboService.myRecords(userId, page, pageSize));
    }

    /** 我的推广 */
    @GetMapping("/seller/promotional/my")
    public Result<?> my(@RequestAttribute Long userId) {
        Map<String, Object> data = promoteService.myPromotion(userId);
        data.put("promoRate1", sysParamService.getString("level_one_rebate_ratio", ""));
        data.put("promoRate2", sysParamService.getString("level_two_rebate_ratio", ""));
        data.put("promoRate3", sysParamService.getString("level_three_rebate_ratio", ""));
        data.put("download", sysParamService.getString("promote_link", ""));
        return Result.ok(data);
    }

    /** 团队推广层级 */
    @GetMapping("/seller/promotional/team-level")
    public Result<?> teamLevel(@RequestAttribute Long userId,
                               @RequestParam(defaultValue = "1") int level) {
        return Result.ok(promoteService.teamInfo(userId));
    }
}
