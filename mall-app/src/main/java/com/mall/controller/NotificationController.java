package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    /** 用户通知分页列表 */
    @GetMapping("/api/notification/list")
    public Result<?> list(@RequestAttribute Long userId,
                          @RequestParam(defaultValue = "1") Integer pageNum,
                          @RequestParam(defaultValue = "20") Integer pageSize,
                          @RequestParam(required = false) String type) {
        return Result.ok(notificationService.list(userId, pageNum, pageSize, type));
    }

    /** 游标滑动列表 (old: message.slidelist) */
    @GetMapping("/api/notification/slide-list")
    public Result<?> slideList(@RequestAttribute Long userId,
                               @RequestParam(defaultValue = "0") Long lastLocation,
                               @RequestParam(defaultValue = "20") Integer pageSize,
                               @RequestParam(required = false) String type) {
        return Result.ok(notificationService.slideList(userId, lastLocation, pageSize, type));
    }

    /** 通知详情 */
    @GetMapping("/api/notification/{id}/detail")
    public Result<?> detail(@RequestAttribute Long userId, @PathVariable Long id) {
        Map<String, Object> data = notificationService.detail(userId, id);
        if (data == null) {
            return Result.fail("通知不存在");
        }
        return Result.ok(data);
    }

    /** 未读数量 */
    @GetMapping("/api/notification/unread")
    public Result<?> unread(@RequestAttribute Long userId,
                            @RequestParam(required = false) Integer type,
                            @RequestParam(required = false) Integer module,
                            @RequestParam(required = false) String language) {
        if (type != null) {
            return Result.ok(notificationService.unreadByType(userId, type, module, language));
        }
        return Result.ok(notificationService.unread(userId));
    }

    /** 标记已读 */
    @PutMapping("/api/notification/{id}/read")
    public Result<?> markRead(@RequestAttribute Long userId, @PathVariable Long id) {
        notificationService.markRead(userId, id);
        return Result.ok();
    }

    /** 批量标记已读 (old: message.read) */
    @PostMapping("/api/notification/read-batch")
    public Result<?> markReadBatch(@RequestAttribute Long userId,
                                   @RequestBody Map<String, String> dto) {
        String ids = dto.get("ids");
        if (ids != null && !ids.isBlank()) {
            List<Long> idList = Arrays.stream(ids.split(","))
                .map(String::trim)
                .filter(s -> !s.isBlank())
                .map(Long::valueOf)
                .collect(Collectors.toList());
            notificationService.markReadBatch(userId, idList);
        }
        return Result.ok();
    }

    /** 全部已读 */
    @PutMapping("/api/notification/read-all")
    public Result<?> markReadAll(@RequestAttribute Long userId) {
        notificationService.markReadAll(userId);
        return Result.ok();
    }

    /** 删除通知 */
    @DeleteMapping("/api/notification/{id}")
    public Result<?> delete(@RequestAttribute Long userId, @PathVariable Long id) {
        notificationService.delete(userId, id);
        return Result.ok();
    }

    /** 管理员发送通知 */
    @PostMapping("/admin/notification/send")
    public Result<?> send(@RequestBody Map<String, Object> dto) {
        Long userId = dto.get("userId") != null
            ? Long.valueOf(dto.get("userId").toString()) : 0L;
        notificationService.send(
            userId,
            (String) dto.get("title"),
            (String) dto.get("content"),
            (String) dto.getOrDefault("type", "SYSTEM").toString(),
            (String) dto.get("relatedId"));
        return Result.ok();
    }

    /** 管理员查看已发送通知列表 */
    @GetMapping("/admin/notification/sent")
    public Result<?> sentList(@RequestParam(defaultValue = "1") Integer pageNum,
                               @RequestParam(defaultValue = "20") Integer pageSize,
                               @RequestParam(required = false) String type,
                               @RequestParam(required = false) String keyword) {
        return Result.ok(notificationService.adminSentList(pageNum, pageSize, type, keyword));
    }
}
