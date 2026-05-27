package com.mall.controller;

import com.mall.common.Result;
import com.mall.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @PostMapping("/send")
    public Result<?> send(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        return Result.ok(chatService.send(userId, dto));
    }

    @GetMapping("/conversations")
    public Result<?> conversations(@RequestAttribute Long userId) {
        return Result.ok(chatService.conversations(userId));
    }

    @GetMapping("/messages/{conversationId}")
    public Result<?> messages(@RequestAttribute Long userId,
                              @PathVariable String conversationId,
                              @RequestParam(required = false) String beforeId,
                              @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(chatService.messages(conversationId, userId, beforeId, pageSize));
    }

    @GetMapping("/unread")
    public Result<?> unread(@RequestAttribute Long userId) {
        return Result.ok(chatService.unread(userId));
    }

    /** 游客发送消息 */
    @PostMapping("/visitor-send")
    public Result<?> visitorSend(@RequestBody Map<String, Object> dto) {
        String ip = (String) dto.get("ip");
        String type = (String) dto.getOrDefault("type", "TEXT").toString();
        String content = (String) dto.get("content");
        if (ip == null || ip.isBlank()) {
            return Result.fail("游客IP不能为空");
        }
        return Result.ok(chatService.visitorSend(ip, type, content));
    }

    /** 检查会话是否存在 */
    @GetMapping("/check")
    public Result<?> checkConversation(@RequestAttribute Long userId,
                                       @RequestParam Long withUserId) {
        return Result.ok(chatService.checkConversation(userId, withUserId));
    }

    /** 发送默认问候消息 */
    @PostMapping("/send-default")
    public Result<?> sendDefault(@RequestAttribute Long userId,
                                 @RequestBody Map<String, Object> dto) {
        Long toUserId = Long.valueOf(dto.get("toUserId").toString());
        String loginType = (String) dto.getOrDefault("loginType", "user").toString();
        String defaultMsg = (String) dto.get("defaultMsg");
        Map<String, Object> result = chatService.sendDefault(userId, toUserId, loginType, defaultMsg);
        return Result.ok(result);
    }

    /** 按角色查未读数 */
    @GetMapping("/unread/{loginType}")
    public Result<?> unreadByLoginType(@RequestAttribute Long userId,
                                       @PathVariable String loginType) {
        return Result.ok(chatService.unreadByLoginType(userId, loginType));
    }

    /** 买家未读数 */
    @GetMapping("/unread/buy")
    public Result<?> buyUnread(@RequestAttribute Long userId) {
        return Result.ok(chatService.buyUnread(userId));
    }

    // === Admin chat endpoints ===

    @GetMapping("/admin/conversations")
    public Result<?> adminConversations(@RequestParam(defaultValue = "1") Integer page,
                                        @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(chatService.adminConversations(page, pageSize));
    }

    @GetMapping("/admin/messages/{conversationId}")
    public Result<?> adminMessages(@PathVariable String conversationId) {
        return Result.ok(chatService.adminMessages(conversationId));
    }

    @PostMapping("/admin/reply")
    public Result<?> adminReply(@RequestBody Map<String, String> dto) {
        return Result.ok(chatService.adminReply(dto.get("conversationId"), dto.get("content")));
    }

    /** 管理后台查看指定会话 (old: onechat) */
    @GetMapping("/admin/onechat")
    public Result<?> adminOneChat(@RequestParam String conversationId,
                                  @RequestParam(required = false) String messageId) {
        return Result.ok(chatService.adminOneChat(conversationId, messageId));
    }
}
