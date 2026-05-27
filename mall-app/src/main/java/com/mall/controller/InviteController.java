package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.InviteService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/invite")
@RequiredArgsConstructor
public class InviteController {

    private final InviteService inviteService;

    @GetMapping("/info")
    public Result<?> inviteInfo(@RequestAttribute Long userId) {
        return Result.ok(inviteService.inviteInfo(userId));
    }

    @GetMapping("/records")
    public Result<?> inviteRecords(@RequestAttribute Long userId,
                                    @RequestParam(defaultValue = "1") Integer pageNum,
                                    @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(inviteService.inviteRecords(userId, pageNum, pageSize));
    }
}
