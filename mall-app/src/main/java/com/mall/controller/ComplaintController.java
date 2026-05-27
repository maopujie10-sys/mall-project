package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/complaint")
@RequiredArgsConstructor
public class ComplaintController {

    private final UserService userService;

    @PostMapping
    public Result<?> submit(@RequestAttribute Long userId, @RequestBody Map<String, Object> body) {
        String type = (String) body.get("type");
        String reason = (String) body.get("reason");
        @SuppressWarnings("unchecked")
        List<String> images = (List<String>) body.get("images");
        String imagesJson = images != null ? String.join(",", images) : "";
        userService.submitComplaint(userId, type, reason, imagesJson);
        return Result.ok();
    }

    @GetMapping("/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") Integer pageNum,
                          @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(userService.complaintList(userId, pageNum, pageSize));
    }
}
