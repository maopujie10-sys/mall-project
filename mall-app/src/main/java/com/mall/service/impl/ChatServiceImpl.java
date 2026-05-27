package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.ChatMessage;
import com.mall.entity.User;
import com.mall.mapper.ChatMessageMapper;
import com.mall.mapper.UserMapper;
import com.mall.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ChatServiceImpl implements ChatService {

    private final ChatMessageMapper chatMessageMapper;
    private final UserMapper userMapper;

    private static final Set<String> VALID_MSG_TYPES = Set.of("TEXT", "IMAGE", "FILE");

    @Override
    @Transactional
    public Map<String, Object> send(Long fromUserId, Map<String, Object> dto) {
        Long toUserId = dto.get("toUserId") != null
            ? Long.valueOf(dto.get("toUserId").toString()) : 0L;

        String conversationId = (String) dto.get("conversationId");
        if (conversationId == null || conversationId.isBlank()) {
            conversationId = buildConversationId(fromUserId, toUserId);
        }

        String content = (String) dto.get("content");
        if (content == null || content.isBlank()) {
            throw new BizException("消息内容不能为空");
        }

        String msgType = (String) dto.getOrDefault("msgType", "TEXT");
        if (!VALID_MSG_TYPES.contains(msgType)) {
            throw new BizException("不支持的消息类型：" + msgType);
        }

        ChatMessage msg = ChatMessage.builder()
            .conversationId(conversationId)
            .fromUserId(fromUserId)
            .toUserId(toUserId)
            .content(content)
            .msgType(msgType)
            .isRead(0)
            .build();
        chatMessageMapper.insert(msg);

        Map<String, Object> result = new HashMap<>();
        result.put("id", msg.getId());
        result.put("conversationId", conversationId);
        result.put("msgType", msg.getMsgType());
        result.put("createTime", msg.getCreateTime());
        return result;
    }

    @Override
    public List<Map<String, Object>> conversations(Long userId) {
        // query conversations where user is a participant
        List<ChatMessage> all = chatMessageMapper.selectList(
            new QueryWrapper<ChatMessage>()
                .and(qw -> qw.eq("from_user_id", userId).or().eq("to_user_id", userId))
                .orderByDesc("create_time"));

        // deduplicate by conversationId, keep latest message
        Map<String, ChatMessage> latest = new LinkedHashMap<>();
        for (ChatMessage m : all) {
            latest.putIfAbsent(m.getConversationId(), m);
        }

        List<Map<String, Object>> result = new ArrayList<>();
        for (ChatMessage m : latest.values()) {
            long unreadCount = chatMessageMapper.selectCount(
                new QueryWrapper<ChatMessage>()
                    .eq("conversation_id", m.getConversationId())
                    .eq("to_user_id", userId)
                    .eq("is_read", 0));

            Map<String, Object> conv = new HashMap<>();
            conv.put("conversationId", m.getConversationId());
            conv.put("lastContent", m.getContent().length() > 50
                ? m.getContent().substring(0, 50) : m.getContent());
            conv.put("lastMsgType", m.getMsgType());
            conv.put("lastTime", m.getCreateTime());
            conv.put("withUserId", m.getFromUserId().equals(userId)
                ? m.getToUserId() : m.getFromUserId());
            conv.put("unreadCount", unreadCount);
            result.add(conv);
        }
        return result;
    }

    @Override
    public List<Map<String, Object>> messages(String conversationId, Long userId,
                                               String beforeId, Integer pageSize) {
        QueryWrapper<ChatMessage> qw = new QueryWrapper<ChatMessage>()
            .eq("conversation_id", conversationId)
            .and(w -> w.eq("from_user_id", userId).or().eq("to_user_id", userId));

        // cursor-based pagination: fetch messages older than beforeId
        if (beforeId != null && !beforeId.isBlank()) {
            ChatMessage anchor = chatMessageMapper.selectById(beforeId);
            if (anchor != null) {
                qw.lt("create_time", anchor.getCreateTime());
            }
        }
        qw.orderByDesc("create_time").last("LIMIT " + pageSize);

        List<ChatMessage> list = chatMessageMapper.selectList(qw);
        // reverse to chronological order
        Collections.reverse(list);

        // mark incoming unread messages as read
        List<Long> idsToMark = list.stream()
            .filter(m -> m.getToUserId().equals(userId) && m.getIsRead() == 0)
            .map(ChatMessage::getId)
            .collect(Collectors.toList());
        if (!idsToMark.isEmpty()) {
            ChatMessage update = new ChatMessage();
            update.setIsRead(1);
            chatMessageMapper.update(update,
                new QueryWrapper<ChatMessage>().in("id", idsToMark));
        }

        return list.stream().map(m -> toMap(m)).collect(Collectors.toList());
    }

    @Override
    public Long unread(Long userId) {
        return chatMessageMapper.countUnread(userId);
    }

    @Override
    @Transactional
    public Map<String, Object> visitorSend(String ip, String type, String content) {
        if (content == null || content.isBlank()) {
            throw new BizException("消息内容不能为空");
        }
        if (!VALID_MSG_TYPES.contains(type != null ? type : "TEXT")) {
            throw new BizException("不支持的消息类型：" + type);
        }
        String conversationId = "visitor_" + ip + "_0";

        ChatMessage msg = ChatMessage.builder()
            .conversationId(conversationId)
            .fromUserId(0L)
            .toUserId(0L)
            .content(content)
            .msgType(type != null ? type : "TEXT")
            .isRead(0)
            .build();
        chatMessageMapper.insert(msg);

        Map<String, Object> result = new HashMap<>();
        result.put("id", msg.getId());
        result.put("conversationId", conversationId);
        result.put("msgType", msg.getMsgType());
        result.put("createTime", msg.getCreateTime());
        return result;
    }

    @Override
    public boolean checkConversation(Long userId1, Long userId2) {
        String convId1 = buildConversationId(userId1, userId2);
        Long count = chatMessageMapper.selectCount(
            new QueryWrapper<ChatMessage>().eq("conversation_id", convId1));
        return count > 0;
    }

    @Override
    @Transactional
    public Map<String, Object> sendDefault(Long fromUserId, Long toUserId, String loginType, String defaultMsg) {
        if (checkConversation(fromUserId, toUserId)) {
            return null; // 会话已存在，不发送默认消息
        }
        String content = defaultMsg != null ? defaultMsg : "Hello, welcome!";
        Map<String, Object> dto = new HashMap<>();
        dto.put("toUserId", toUserId);
        dto.put("content", content);
        dto.put("msgType", "TEXT");

        // fromUserId depends on loginType
        Long actualFrom = "shop".equals(loginType) ? toUserId : fromUserId;
        return send(actualFrom, dto);
    }

    @Override
    public Long unreadByLoginType(Long userId, String loginType) {
        // "shop" - seller sees all unread (sent to them as toUserId)
        // "user" - buyer sees unread from sellers only
        QueryWrapper<ChatMessage> qw = new QueryWrapper<ChatMessage>()
            .eq("to_user_id", userId)
            .eq("is_read", 0);
        if ("user".equals(loginType)) {
            // user only counts messages from platform/sellers (fromUserId=0 or seller)
            qw.in("from_user_id", 0L);
        }
        return chatMessageMapper.selectCount(qw);
    }

    @Override
    public Long buyUnread(Long userId) {
        QueryWrapper<ChatMessage> qw = new QueryWrapper<ChatMessage>()
            .eq("to_user_id", userId)
            .eq("is_read", 0);
        return chatMessageMapper.selectCount(qw);
    }

    // ===== Admin =====

    @Override
    public Map<String, Object> adminConversations(Integer page, Integer pageSize) {
        IPage<ChatMessage> pg = chatMessageMapper.selectPage(
            new Page<>(page, pageSize),
            new QueryWrapper<ChatMessage>()
                .select("DISTINCT conversation_id, MAX(create_time) as create_time, " +
                        "MAX(from_user_id) as from_user_id, MAX(to_user_id) as to_user_id, " +
                        "MAX(content) as content, MAX(msg_type) as msg_type")
                .groupBy("conversation_id")
                .orderByDesc("create_time"));

        List<Map<String, Object>> list = new ArrayList<>();
        for (ChatMessage m : pg.getRecords()) {
            long unreadCount = chatMessageMapper.selectCount(
                new QueryWrapper<ChatMessage>()
                    .eq("conversation_id", m.getConversationId())
                    .eq("is_read", 0));
            Map<String, Object> conv = new HashMap<>();
            conv.put("conversationId", m.getConversationId());
            conv.put("lastContent", m.getContent() != null && m.getContent().length() > 50
                ? m.getContent().substring(0, 50) : m.getContent());
            conv.put("lastMsgType", m.getMsgType());
            conv.put("lastTime", m.getCreateTime());
            conv.put("unreadCount", unreadCount);
            conv.put("fromUserId", m.getFromUserId());
            conv.put("toUserId", m.getToUserId());
            list.add(conv);
        }
        Map<String, Object> result = new HashMap<>();
        result.put("records", list);
        result.put("total", pg.getTotal());
        result.put("page", pg.getCurrent());
        return result;
    }

    @Override
    public List<Map<String, Object>> adminMessages(String conversationId) {
        List<ChatMessage> list = chatMessageMapper.selectList(
            new QueryWrapper<ChatMessage>()
                .eq("conversation_id", conversationId)
                .orderByAsc("create_time"));
        return list.stream().map(m -> toMap(m)).collect(Collectors.toList());
    }

    @Override
    @Transactional
    public Map<String, Object> adminReply(String conversationId, String content) {
        if (content == null || content.isBlank()) {
            throw new BizException("回复内容不能为空");
        }
        ChatMessage msg = ChatMessage.builder()
            .conversationId(conversationId)
            .fromUserId(0L)
            .toUserId(0L)
            .content(content)
            .msgType("TEXT")
            .isRead(0)
            .createTime(LocalDateTime.now())
            .build();
        chatMessageMapper.insert(msg);
        return toMap(msg);
    }

    @Override
    public List<Map<String, Object>> adminOneChat(String conversationId, String messageId) {
        QueryWrapper<ChatMessage> qw = new QueryWrapper<ChatMessage>()
            .eq("conversation_id", conversationId)
            .orderByAsc("create_time");
        // cursor: fetch older than messageId
        if (messageId != null && !messageId.isBlank()) {
            ChatMessage anchor = chatMessageMapper.selectById(messageId);
            if (anchor != null) {
                qw.lt("create_time", anchor.getCreateTime());
            }
        }
        qw.last("LIMIT 30");
        List<ChatMessage> list = chatMessageMapper.selectList(qw);
        return list.stream().map(m -> toMap(m)).collect(Collectors.toList());
    }

    private Map<String, Object> toMap(ChatMessage m) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", m.getId());
        map.put("conversationId", m.getConversationId());
        map.put("fromUserId", m.getFromUserId());
        map.put("toUserId", m.getToUserId());
        map.put("content", m.getContent());
        map.put("msgType", m.getMsgType());
        map.put("isRead", m.getIsRead());
        map.put("createTime", m.getCreateTime());
        return map;
    }

    private String buildConversationId(Long userId1, Long userId2) {
        return userId1 < userId2
            ? userId1 + "_" + userId2
            : userId2 + "_" + userId1;
    }
}
