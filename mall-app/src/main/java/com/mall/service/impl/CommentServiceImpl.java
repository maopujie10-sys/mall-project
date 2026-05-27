package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.MallComment;
import com.mall.mapper.MallCommentMapper;
import com.mall.service.CommentService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
@RequiredArgsConstructor
public class CommentServiceImpl implements CommentService {

    private final MallCommentMapper commentMapper;

    @Override
    public Map<String, Object> listByGoodId(String goodId, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        Page<MallComment> pg = new Page<>(p, ps);
        Page<MallComment> result = commentMapper.selectPage(pg,
            new QueryWrapper<MallComment>().eq("good_id", goodId).orderByDesc("date"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallComment c : result.getRecords()) list.add(toMap(c));
        Map<String, Object> r = new HashMap<>();
        r.put("total", result.getTotal());
        r.put("page", p);
        r.put("pageSize", ps);
        r.put("list", list);
        return r;
    }

    @Override
    public void add(Long userId, Map<String, Object> dto) {
        String goodId = (String) dto.get("goodId");
        String content = (String) dto.get("content");
        if (goodId == null || goodId.isEmpty()) throw new BizException("商品ID不能为空");
        if (content == null || content.isEmpty()) throw new BizException("评论内容不能为空");

        MallComment comment = new MallComment();
        comment.setUuid(UUID.randomUUID().toString().replace("-", ""));
        comment.setGoodId(goodId);
        comment.setUsername((String) dto.getOrDefault("username", userId.toString()));
        comment.setCategory((String) dto.getOrDefault("category", "5"));
        comment.setContent(content);
        comment.setDate(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        commentMapper.insert(comment);
    }

    @Override
    public void delete(Long userId, String uuid) {
        MallComment comment = commentMapper.selectById(uuid);
        if (comment == null) throw new BizException("评论不存在");
        commentMapper.deleteById(uuid);
    }

    private Map<String, Object> toMap(MallComment c) {
        Map<String, Object> m = new HashMap<>();
        m.put("uuid", c.getUuid());
        m.put("goodId", c.getGoodId());
        m.put("username", c.getUsername());
        m.put("category", c.getCategory());
        m.put("content", c.getContent());
        m.put("date", c.getDate());
        return m;
    }
}
