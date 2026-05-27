package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.Subscribe;
import com.mall.mapper.SubscribeMapper;
import com.mall.service.SubscribeService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class SubscribeServiceImpl implements SubscribeService {

    private final SubscribeMapper subscribeMapper;

    private static final List<String> VALID_TYPES = List.of("ORDER", "SYSTEM", "PROMOTION", "CHAT");

    @Override
    @Transactional
    public void subscribe(Long userId, Map<String, Object> dto) {
        String type = (String) dto.get("type");
        if (type == null || !VALID_TYPES.contains(type)) {
            throw new BizException("无效的订阅类型");
        }
        String target = (String) dto.getOrDefault("target", "");
        String channel = (String) dto.getOrDefault("channel", "APP");

        Subscribe exist = subscribeMapper.selectOne(
            new QueryWrapper<Subscribe>()
                .eq("user_id", userId)
                .eq("type", type)
                .eq("target", target));
        if (exist != null) {
            exist.setEnabled(1);
            exist.setChannel(channel);
            subscribeMapper.updateById(exist);
            return;
        }

        Subscribe sub = Subscribe.builder()
            .userId(userId).type(type).target(target)
            .channel(channel).enabled(1).build();
        subscribeMapper.insert(sub);
    }

    @Override
    public List<Map<String, Object>> list(Long userId) {
        List<Subscribe> list = subscribeMapper.selectList(
            new QueryWrapper<Subscribe>().eq("user_id", userId).orderByDesc("create_time"));
        return list.stream().map(s -> {
            Map<String, Object> m = new HashMap<>();
            m.put("id", s.getId());
            m.put("type", s.getType());
            m.put("target", s.getTarget());
            m.put("channel", s.getChannel());
            m.put("enabled", s.getEnabled());
            m.put("createTime", s.getCreateTime());
            return m;
        }).collect(Collectors.toList());
    }

    @Override
    @Transactional
    public void update(Long userId, Long id, Map<String, Object> dto) {
        Subscribe sub = subscribeMapper.selectOne(
            new QueryWrapper<Subscribe>().eq("id", id).eq("user_id", userId));
        if (sub == null) throw new BizException("订阅记录不存在");

        if (dto.containsKey("enabled")) {
            sub.setEnabled((Integer) dto.get("enabled"));
        }
        if (dto.containsKey("channel")) {
            sub.setChannel((String) dto.get("channel"));
        }
        subscribeMapper.updateById(sub);
    }

    @Override
    @Transactional
    public void delete(Long userId, Long id) {
        Subscribe sub = subscribeMapper.selectOne(
            new QueryWrapper<Subscribe>().eq("id", id).eq("user_id", userId));
        if (sub == null) throw new BizException("订阅记录不存在");
        subscribeMapper.deleteById(id);
    }

    // ======================== Admin Methods ========================

    @Override
    public Map<String, Object> adminList(String email, String startTime, String endTime, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<Subscribe> qw = new QueryWrapper<>();
        if (email != null && !email.isEmpty()) qw.like("target", email);
        qw.orderByDesc("create_time");
        Page<Subscribe> pg = new Page<>(p, ps);
        Page<Subscribe> result = subscribeMapper.selectPage(pg, qw);
        Map<String, Object> r = new HashMap<>();
        r.put("total", result.getTotal());
        r.put("page", p);
        r.put("pageSize", ps);
        r.put("list", result.getRecords().stream().map(s -> {
            Map<String, Object> m = new HashMap<>();
            m.put("id", s.getId());
            m.put("userId", s.getUserId());
            m.put("type", s.getType());
            m.put("target", s.getTarget());
            m.put("channel", s.getChannel());
            m.put("enabled", s.getEnabled());
            m.put("createTime", s.getCreateTime());
            return m;
        }).collect(Collectors.toList()));
        return r;
    }

    @Override
    @Transactional
    public void adminDelete(Long id) {
        Subscribe sub = subscribeMapper.selectById(id);
        if (sub == null) throw new BizException("订阅记录不存在");
        subscribeMapper.deleteById(id);
    }

    @Override
    public void adminPush(Map<String, Object> dto) {
        String type = (String) dto.getOrDefault("type", "SYSTEM");
        String message = (String) dto.get("message");
        if (message == null || message.isEmpty()) throw new BizException("推送内容不能为空");
        // Get all enabled subscribers of this type
        List<Subscribe> list = subscribeMapper.selectList(
            new QueryWrapper<Subscribe>().eq("type", type).eq("enabled", 1));
        // In production, this would integrate with push notification service (FCM/APNs/email)
        // For now, log the push event
        System.out.println("Admin push to " + list.size() + " subscribers: " + message);
    }
}
