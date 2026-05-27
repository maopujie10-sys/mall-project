package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.Notification;
import com.mall.mapper.NotificationMapper;
import com.mall.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class NotificationServiceImpl implements NotificationService {

    private final NotificationMapper notificationMapper;

    @Override
    public Map<String, Object> list(Long userId, Integer pageNum, Integer pageSize, String type) {
        QueryWrapper<Notification> qw = new QueryWrapper<Notification>()
            .and(w -> w.eq("user_id", userId).or().eq("user_id", 0))
            .orderByDesc("create_time");
        if (type != null && !type.isBlank()) {
            qw.eq("type", type);
        }
        IPage<Notification> page = notificationMapper.selectPage(new Page<>(pageNum, pageSize), qw);

        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("page", pageNum);
        result.put("pageSize", pageSize);
        result.put("list", page.getRecords().stream().map(this::toMap).collect(Collectors.toList()));
        return result;
    }

    @Override
    public Long unread(Long userId) {
        return notificationMapper.selectCount(
            new QueryWrapper<Notification>()
                .eq("user_id", userId)
                .eq("is_read", 0));
    }

    @Override
    public Long unreadByType(Long userId, Integer type, Integer module, String language) {
        QueryWrapper<Notification> qw = new QueryWrapper<Notification>()
            .eq("user_id", userId)
            .eq("is_read", 0);
        if (type != null) {
            qw.eq("type", type);
        }
        return notificationMapper.selectCount(qw);
    }

    @Override
    public Map<String, Object> detail(Long userId, Long id) {
        Notification n = notificationMapper.selectById(id);
        if (n == null) return null;
        if (!n.getUserId().equals(userId) && !n.getUserId().equals(0L)) {
            throw new BizException("无权查看此通知");
        }
        return toMap(n);
    }

    @Override
    @Transactional
    public void markRead(Long userId, Long id) {
        Notification n = notificationMapper.selectById(id);
        if (n == null) throw new BizException("通知不存在");
        if (!n.getUserId().equals(userId) && !n.getUserId().equals(0L)) {
            throw new BizException("无权操作此通知");
        }
        if (n.getUserId().equals(0L)) {
            Notification copy = Notification.builder()
                .userId(userId).title(n.getTitle()).content(n.getContent())
                .type(n.getType()).relatedId(n.getRelatedId()).isRead(1).build();
            notificationMapper.insert(copy);
        } else {
            n.setIsRead(1);
            notificationMapper.updateById(n);
        }
    }

    @Override
    @Transactional
    public void markReadBatch(Long userId, List<Long> ids) {
        for (Long id : ids) {
            Notification n = notificationMapper.selectById(id);
            if (n == null) continue;
            if (!n.getUserId().equals(userId) && !n.getUserId().equals(0L)) {
                continue;
            }
            if (n.getUserId().equals(0L)) {
                Notification copy = Notification.builder()
                    .userId(userId).title(n.getTitle()).content(n.getContent())
                    .type(n.getType()).relatedId(n.getRelatedId()).isRead(1).build();
                notificationMapper.insert(copy);
            } else {
                n.setIsRead(1);
                notificationMapper.updateById(n);
            }
        }
    }

    @Override
    @Transactional
    public void markReadAll(Long userId) {
        // mark all personal unread notifications
        List<Notification> unreadList = notificationMapper.selectList(
            new QueryWrapper<Notification>().eq("user_id", userId).eq("is_read", 0));
        for (Notification n : unreadList) {
            n.setIsRead(1);
            notificationMapper.updateById(n);
        }
        // mark global notifications as read by creating personal copies
        List<Notification> globalList = notificationMapper.selectList(
            new QueryWrapper<Notification>().eq("user_id", 0));
        for (Notification g : globalList) {
            Long exists = notificationMapper.selectCount(
                new QueryWrapper<Notification>()
                    .eq("user_id", userId)
                    .eq("title", g.getTitle())
                    .eq("type", g.getType()));
            if (exists == 0) {
                Notification copy = Notification.builder()
                    .userId(userId).title(g.getTitle()).content(g.getContent())
                    .type(g.getType()).relatedId(g.getRelatedId()).isRead(1).build();
                notificationMapper.insert(copy);
            }
        }
    }

    @Override
    @Transactional
    public void delete(Long userId, Long id) {
        Notification n = notificationMapper.selectById(id);
        if (n == null) return;
        if (!n.getUserId().equals(userId)) throw new BizException("无权删除此通知");
        notificationMapper.deleteById(id);
    }

    @Override
    public List<Map<String, Object>> slideList(Long userId, Long lastLocation, Integer pageSize, String type) {
        QueryWrapper<Notification> qw = new QueryWrapper<Notification>()
            .and(w -> w.eq("user_id", userId).or().eq("user_id", 0))
            .orderByDesc("create_time");
        if (type != null && !type.isBlank()) {
            qw.eq("type", type);
        }
        if (lastLocation != null && lastLocation > 0) {
            qw.lt("id", lastLocation);
        }
        qw.last("LIMIT " + pageSize);
        List<Notification> list = notificationMapper.selectList(qw);
        return list.stream().map(this::toMap).collect(Collectors.toList());
    }

    @Override
    @Transactional
    public void send(Long userId, String title, String content, String type, String relatedId) {
        Notification n = Notification.builder()
            .userId(userId).title(title).content(content)
            .type(type != null ? type : "SYSTEM")
            .relatedId(relatedId).isRead(0).build();
        notificationMapper.insert(n);
    }

    // === Admin ===

    @Override
    public Map<String, Object> adminSentList(Integer pageNum, Integer pageSize, String type, String keyword) {
        QueryWrapper<Notification> qw = new QueryWrapper<>();
        if (type != null && !type.isBlank()) {
            qw.eq("type", type);
        }
        if (keyword != null && !keyword.isBlank()) {
            qw.and(w -> w.like("title", keyword).or().like("content", keyword));
        }
        qw.orderByDesc("create_time");
        IPage<Notification> page = notificationMapper.selectPage(new Page<>(pageNum, pageSize), qw);
        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("page", pageNum);
        result.put("pageSize", pageSize);
        result.put("list", page.getRecords().stream().map(this::toMap).collect(Collectors.toList()));
        return result;
    }

    private Map<String, Object> toMap(Notification n) {
        Map<String, Object> m = new HashMap<>();
        m.put("id", n.getId());
        m.put("title", n.getTitle());
        m.put("content", n.getContent());
        m.put("type", n.getType());
        m.put("relatedId", n.getRelatedId());
        m.put("isRead", n.getIsRead());
        m.put("createTime", n.getCreateTime());
        return m;
    }
}
