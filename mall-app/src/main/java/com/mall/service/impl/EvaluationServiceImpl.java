package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.exception.BizException;
import com.mall.entity.MallEvaluation;
import com.mall.mapper.MallEvaluationMapper;
import com.mall.service.EvaluationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class EvaluationServiceImpl implements EvaluationService {

    private final MallEvaluationMapper evaluationMapper;

    @Override
    public List<Map<String, Object>> listByProduct(String sellerGoodsId, int page, int pageSize, Integer evaluationType) {
        Page<MallEvaluation> p = new Page<>(page, pageSize);
        QueryWrapper<MallEvaluation> w = new QueryWrapper<MallEvaluation>()
            .eq("seller_goods_id", sellerGoodsId)
            .eq("status", 1);
        if (evaluationType != null) {
            if (evaluationType == -2) {
                // has picture filter
                w.and(wr -> wr.isNotNull("IMG_URL_1").or().isNotNull("IMG_URL_2").or().isNotNull("IMG_URL_3"));
            } else {
                w.eq("evaluation_type", evaluationType);
            }
        }
        w.orderByDesc("create_time");
        Page<MallEvaluation> result = evaluationMapper.selectPage(p, w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallEvaluation e : result.getRecords()) {
            list.add(toMap(e));
        }
        return list;
    }

    @Override
    public Map<String, Object> countByType(String sellerGoodsId) {
        QueryWrapper<MallEvaluation> w = new QueryWrapper<MallEvaluation>()
            .eq("seller_goods_id", sellerGoodsId)
            .eq("status", 1);
        long total = evaluationMapper.selectCount(w);
        long havePicture = evaluationMapper.selectCount(
            new QueryWrapper<MallEvaluation>()
                .eq("seller_goods_id", sellerGoodsId).eq("status", 1)
                .and(wr -> wr.isNotNull("IMG_URL_1").or().isNotNull("IMG_URL_2").or().isNotNull("IMG_URL_3")));
        long positive = evaluationMapper.selectCount(
            new QueryWrapper<MallEvaluation>()
                .eq("seller_goods_id", sellerGoodsId).eq("status", 1).eq("evaluation_type", 1));
        long medium = evaluationMapper.selectCount(
            new QueryWrapper<MallEvaluation>()
                .eq("seller_goods_id", sellerGoodsId).eq("status", 1).eq("evaluation_type", 2));
        long negative = evaluationMapper.selectCount(
            new QueryWrapper<MallEvaluation>()
                .eq("seller_goods_id", sellerGoodsId).eq("status", 1).eq("evaluation_type", 3));
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("evaluationNum", total);
        map.put("havePicture", havePicture);
        map.put("positiveComments", positive);
        map.put("mediumReview", medium);
        map.put("negativeComment", negative);
        return map;
    }

    @Override
    public List<Map<String, Object>> listByUser(Long userId, int page, int pageSize) {
        String partyId = userId.toString();
        Page<MallEvaluation> p = new Page<>(page, pageSize);
        Page<MallEvaluation> result = evaluationMapper.selectPage(p,
            new QueryWrapper<MallEvaluation>()
                .eq("party_id", partyId)
                .orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallEvaluation e : result.getRecords()) {
            list.add(toMap(e));
        }
        return list;
    }

    @Override
    public List<Map<String, Object>> listBySeller(String sellerId, int page, int pageSize) {
        Page<MallEvaluation> p = new Page<>(page, pageSize);
        Page<MallEvaluation> result = evaluationMapper.selectPage(p,
            new QueryWrapper<MallEvaluation>()
                .eq("seller_id", sellerId)
                .eq("status", 1)
                .orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallEvaluation e : result.getRecords()) {
            list.add(toMap(e));
        }
        return list;
    }

    @Override
    public Map<String, Object> detail(String uuid) {
        MallEvaluation e = evaluationMapper.selectById(uuid);
        if (e == null) throw new BizException("评价不存在");
        return toMap(e);
    }

    @Override
    @Transactional
    public void create(Long userId, Map<String, Object> dto) {
        String partyId = userId.toString();
        String sellerGoodsId = (String) dto.get("sellerGoodsId");
        String orderId = (String) dto.get("orderId");

        if (sellerGoodsId == null || sellerGoodsId.isBlank()) throw new BizException("商品ID不能为空");
        if (orderId == null || orderId.isBlank()) throw new BizException("订单ID不能为空");

        Integer rating = (Integer) dto.getOrDefault("rating", 5);
        if (rating < 1 || rating > 5) throw new BizException("评分需在1-5之间");

        long count = evaluationMapper.selectCount(
            new QueryWrapper<MallEvaluation>()
                .eq("party_id", partyId)
                .eq("order_id", orderId)
                .eq("seller_goods_id", sellerGoodsId));
        if (count > 0) throw new BizException("该订单商品已评价");

        MallEvaluation e = new MallEvaluation();
        e.setUuid(UUID.randomUUID().toString().replace("-", ""));
        e.setPartyId(partyId);
        e.setUserName((String) dto.getOrDefault("userName", "User" + partyId));
        e.setSellerGoodsId(sellerGoodsId);
        e.setSellerId((String) dto.getOrDefault("sellerId", ""));
        e.setOrderId(orderId);
        e.setSkuId((String) dto.getOrDefault("skuId", ""));
        e.setSystemGoodsId((String) dto.getOrDefault("systemGoodsId", ""));
        e.setContent((String) dto.getOrDefault("content", ""));
        e.setRating(rating);
        e.setEvaluationType((Integer) dto.getOrDefault("evaluationType", 1));
        e.setStatus(1);
        e.setGoodsStatus(1);
        e.setCreateTime(LocalDateTime.now());
        e.setEvaluationTime(LocalDateTime.now());
        e.setSourceType((Integer) dto.getOrDefault("sourceType", 1));

        if (dto.containsKey("imgUrl1")) e.setImgUrl1((String) dto.get("imgUrl1"));
        if (dto.containsKey("imgUrl2")) e.setImgUrl2((String) dto.get("imgUrl2"));
        if (dto.containsKey("imgUrl3")) e.setImgUrl3((String) dto.get("imgUrl3"));
        if (dto.containsKey("imgUrl4")) e.setImgUrl4((String) dto.get("imgUrl4"));
        if (dto.containsKey("imgUrl5")) e.setImgUrl5((String) dto.get("imgUrl5"));
        if (dto.containsKey("imgUrl6")) e.setImgUrl6((String) dto.get("imgUrl6"));
        if (dto.containsKey("imgUrl7")) e.setImgUrl7((String) dto.get("imgUrl7"));
        if (dto.containsKey("imgUrl8")) e.setImgUrl8((String) dto.get("imgUrl8"));
        if (dto.containsKey("imgUrl9")) e.setImgUrl9((String) dto.get("imgUrl9"));

        evaluationMapper.insert(e);
    }

    @Override
    public void delete(Long userId, String uuid) {
        String partyId = userId.toString();
        MallEvaluation e = evaluationMapper.selectOne(
            new QueryWrapper<MallEvaluation>().eq("uuid", uuid).eq("party_id", partyId));
        if (e == null) throw new BizException("评价不存在");
        e.setStatus(0);
        evaluationMapper.updateById(e);
    }

    private Map<String, Object> toMap(MallEvaluation e) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("uuid", e.getUuid());
        map.put("userName", e.getUserName());
        map.put("partyId", e.getPartyId());
        map.put("sellerGoodsId", e.getSellerGoodsId());
        map.put("sellerId", e.getSellerId());
        map.put("orderId", e.getOrderId());
        map.put("skuId", e.getSkuId());
        map.put("systemGoodsId", e.getSystemGoodsId());
        map.put("content", e.getContent());
        map.put("rating", e.getRating());
        map.put("evaluationType", e.getEvaluationType());
        map.put("goodsStatus", e.getGoodsStatus());
        map.put("sourceType", e.getSourceType());
        map.put("imgUrl1", e.getImgUrl1());
        map.put("imgUrl2", e.getImgUrl2());
        map.put("imgUrl3", e.getImgUrl3());
        map.put("imgUrl4", e.getImgUrl4());
        map.put("imgUrl5", e.getImgUrl5());
        map.put("imgUrl6", e.getImgUrl6());
        map.put("imgUrl7", e.getImgUrl7());
        map.put("imgUrl8", e.getImgUrl8());
        map.put("imgUrl9", e.getImgUrl9());
        map.put("createTime", e.getCreateTime());
        map.put("evaluationTime", e.getEvaluationTime());
        return map;
    }

    // === Admin ===

    @Override
    public Map<String, Object> adminList(String keyword, Integer status, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallEvaluation> w = new QueryWrapper<>();
        if (StringUtils.hasText(keyword)) {
            w.and(wr -> wr.like("user_name", keyword).or().like("content", keyword).or().like("seller_goods_id", keyword));
        }
        if (status != null) w.eq("status", status);
        w.orderByDesc("create_time");
        IPage<MallEvaluation> pg = evaluationMapper.selectPage(new Page<>(p, ps), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallEvaluation e : pg.getRecords()) {
            list.add(toMap(e));
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", p);
        result.put("pageSize", ps);
        result.put("list", list);
        return result;
    }

    @Override
    public void adminUpdateStatus(String uuid, Integer status) {
        MallEvaluation e = evaluationMapper.selectById(uuid);
        if (e == null) throw new BizException("评价不存在");
        e.setStatus(status);
        evaluationMapper.updateById(e);
    }

    @Override
    public void adminDelete(String uuid) {
        MallEvaluation e = evaluationMapper.selectById(uuid);
        if (e == null) throw new BizException("评价不存在");
        evaluationMapper.deleteById(uuid);
    }

    // === System Comment ===

    @Override
    public Map<String, Object> systemCommentList(String systemGoodsId, Integer status, Integer page, Integer pageSize) {
        int p = page == null || page < 1 ? 1 : page;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<MallEvaluation> w = new QueryWrapper<>();
        if (systemGoodsId != null && !systemGoodsId.isEmpty()) w.eq("system_goods_id", systemGoodsId);
        if (status != null && status != -2) w.eq("status", status);
        w.orderByDesc("create_time");
        IPage<MallEvaluation> pg = evaluationMapper.selectPage(new Page<>(p, ps), w);
        List<Map<String, Object>> list = new ArrayList<>();
        for (MallEvaluation e : pg.getRecords()) {
            list.add(toMap(e));
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("total", pg.getTotal());
        result.put("page", p);
        result.put("pageSize", ps);
        result.put("list", list);
        return result;
    }

    @Override
    @Transactional
    public void systemCommentSave(Map<String, Object> dto) {
        String id = (String) dto.get("id");
        MallEvaluation e;
        if (id != null && !id.isEmpty()) {
            e = evaluationMapper.selectById(id);
            if (e == null) throw new BizException("系统评论不存在");
        } else {
            e = new MallEvaluation();
            e.setUuid(UUID.randomUUID().toString().replace("-", ""));
            e.setCreateTime(LocalDateTime.now());
            e.setSourceType(1); // system comment
        }
        if (dto.containsKey("content")) e.setContent((String) dto.get("content"));
        if (dto.containsKey("rating")) e.setRating((Integer) dto.get("rating"));
        if (dto.containsKey("systemGoodsId")) e.setSystemGoodsId((String) dto.get("systemGoodsId"));
        if (dto.containsKey("userName")) e.setUserName((String) dto.get("userName"));
        if (dto.containsKey("status")) e.setStatus((Integer) dto.get("status"));
        if (dto.containsKey("imgUrl1")) e.setImgUrl1((String) dto.get("imgUrl1"));
        if (dto.containsKey("imgUrl2")) e.setImgUrl2((String) dto.get("imgUrl2"));
        if (dto.containsKey("imgUrl3")) e.setImgUrl3((String) dto.get("imgUrl3"));
        if (id != null && !id.isEmpty()) {
            evaluationMapper.updateById(e);
        } else {
            evaluationMapper.insert(e);
        }
    }

    @Override
    public void systemCommentUpdateStatus(String id, Integer status) {
        MallEvaluation e = evaluationMapper.selectById(id);
        if (e == null) throw new BizException("系统评论不存在");
        e.setStatus(status);
        evaluationMapper.updateById(e);
    }

    @Override
    public void systemCommentDelete(String id) {
        MallEvaluation e = evaluationMapper.selectById(id);
        if (e == null) throw new BizException("系统评论不存在");
        evaluationMapper.deleteById(id);
    }
}
