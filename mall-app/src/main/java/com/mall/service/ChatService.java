package com.mall.service;

import java.util.List;
import java.util.Map;

public interface ChatService {
    Map<String, Object> send(Long fromUserId, Map<String, Object> dto);
    List<Map<String, Object>> conversations(Long userId);
    List<Map<String, Object>> messages(String conversationId, Long userId, String beforeId, Integer pageSize);
    Long unread(Long userId);

    /** 游客IP发送消息 */
    Map<String, Object> visitorSend(String ip, String type, String content);
    /** 检查会话是否存在 */
    boolean checkConversation(Long userId1, Long userId2);
    /** 发送默认问候消息 */
    Map<String, Object> sendDefault(Long fromUserId, Long toUserId, String loginType, String defaultMsg);
    /** 按角色查未读数 (user/shop) */
    Long unreadByLoginType(Long userId, String loginType);
    /** 买家未读数 */
    Long buyUnread(Long userId);

    // Admin
    Map<String, Object> adminConversations(Integer page, Integer pageSize);
    List<Map<String, Object>> adminMessages(String conversationId);
    Map<String, Object> adminReply(String conversationId, String content);
    /** 管理后台查看指定会话 */
    List<Map<String, Object>> adminOneChat(String conversationId, String messageId);
}
