package com.mall.controller.merchant;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.Result;
import com.mall.entity.*;
import com.mall.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 商家端-评价管理（迁移自旧商城 SellerEvaluationController）
 * 评价列表含商品信息/用户头像脱敏/评价统计/评分分布
 */
@RestController
@RequestMapping("/merchant")
@RequiredArgsConstructor
public class MerchantEvaluationController {

    private final MallEvaluationMapper evaluationMapper;
    private final SellerGoodsMapper sellerGoodsMapper;
    private final SystemGoodsMapper systemGoodsMapper;
    private final UserMapper userMapper;
    private final MerchantMapper merchantMapper;

    /**
     * 评价详细列表（含商品信息、用户头像、脱敏用户名、评分筛选）
     */
    @GetMapping("/evaluation/list")
    public Result<?> evaluationList(@RequestAttribute Long userId,
                                    @RequestParam(defaultValue = "1") Integer pageNum,
                                    @RequestParam(defaultValue = "10") Integer pageSize,
                                    @RequestParam(required = false) String userName,
                                    @RequestParam(required = false) Integer evaluationType) {

        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        String sellerId = String.valueOf(merchant.getUserId());

        QueryWrapper<MallEvaluation> qw = new QueryWrapper<>();
        qw.eq("seller_id", sellerId);
        qw.eq("status", 0);
        if (userName != null && !userName.isBlank()) {
            qw.like("user_name", userName);
        }
        if (evaluationType != null) {
            qw.eq("evaluation_type", evaluationType);
        }
        qw.orderByDesc("create_time");

        Page<MallEvaluation> page = new Page<>(pageNum, pageSize);
        Page<MallEvaluation> result = evaluationMapper.selectPage(page, qw);

        List<Map<String, Object>> list = result.getRecords().stream().map(eval -> {
            Map<String, Object> m = new HashMap<>();
            m.put("uuid", eval.getUuid());
            m.put("userName", desensitize(eval.getUserName()));
            m.put("rating", eval.getRating());
            m.put("content", eval.getContent());
            m.put("evaluationType", eval.getEvaluationType());
            m.put("evaluationTime", eval.getEvaluationTime() != null ?
                    eval.getEvaluationTime().toString() : "");
            m.put("commentTime", eval.getEvaluationTime() != null ?
                    eval.getEvaluationTime().toString() : eval.getCreateTime().toString());
            m.put("avatar", eval.getPartyAvatar());
            m.put("partyName", eval.getPartyName());
            m.put("orderId", eval.getOrderId());
            m.put("skuId", eval.getSkuId());

            // 评价图片
            List<String> images = new ArrayList<>();
            if (eval.getImgUrl1() != null) images.add(eval.getImgUrl1());
            if (eval.getImgUrl2() != null) images.add(eval.getImgUrl2());
            if (eval.getImgUrl3() != null) images.add(eval.getImgUrl3());
            m.put("images", images);

            // 关联商品信息
            if (eval.getSellerGoodsId() != null) {
                SellerGoods sellerGoods = sellerGoodsMapper.selectById(eval.getSellerGoodsId());
                if (sellerGoods != null) {
                    Map<String, Object> goodsInfo = new HashMap<>();
                    goodsInfo.put("id", sellerGoods.getUuid());
                    goodsInfo.put("sellerId", sellerGoods.getSellerId());
                    goodsInfo.put("goodsName", sellerGoods.getGoodsName());
                    goodsInfo.put("coverImg", sellerGoods.getCoverImg());
                    goodsInfo.put("price", sellerGoods.getPrice());

                    if (sellerGoods.getSystemGoodsId() != null) {
                        SystemGoods sysGoods = systemGoodsMapper.selectById(sellerGoods.getSystemGoodsId());
                        if (sysGoods != null) {
                            goodsInfo.put("imgUrl1", sysGoods.getMainImage());
                        }
                    }
                    m.put("goodsVo", goodsInfo);
                }
            }

            // 用户头像fallback
            if (eval.getPartyId() != null && (eval.getPartyAvatar() == null || eval.getPartyAvatar().isBlank())) {
                try {
                    User user = userMapper.selectById(Long.valueOf(eval.getPartyId()));
                    if (user != null) {
                        m.put("avatar", user.getAvatar());
                        m.put("partyName", user.getNickname());
                    }
                } catch (NumberFormatException ignored) {}
            }

            return m;
        }).collect(Collectors.toList());

        Map<String, Object> data = new HashMap<>();
        data.put("pageInfo", Map.of("pageNum", pageNum, "pageSize", pageSize, "totalElements", result.getTotal()));
        data.put("pageList", list);
        return Result.ok(data);
    }

    /**
     * 评价统计概览（好评率/各星级分布）
     */
    @GetMapping("/evaluation/stats")
    public Result<?> evaluationStats(@RequestAttribute Long userId) {
        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        String sellerId = String.valueOf(merchant.getUserId());

        QueryWrapper<MallEvaluation> qw = new QueryWrapper<>();
        qw.eq("seller_id", sellerId);
        qw.eq("status", 0);
        Long totalCount = evaluationMapper.selectCount(qw);

        Map<Integer, Long> distribution = new LinkedHashMap<>();
        distribution.put(5, 0L);
        distribution.put(4, 0L);
        distribution.put(3, 0L);
        distribution.put(2, 0L);
        distribution.put(1, 0L);
        double avgRating = 0;

        if (totalCount > 0) {
            List<MallEvaluation> all = evaluationMapper.selectList(qw);
            avgRating = all.stream().mapToInt(e -> e.getRating() != null ? e.getRating() : 0)
                    .average().orElse(0);
            for (MallEvaluation e : all) {
                int r = e.getRating() != null ? e.getRating() : 0;
                if (r >= 1 && r <= 5) {
                    distribution.merge(r, 1L, Long::sum);
                }
            }
        }

        Map<String, Object> data = new HashMap<>();
        data.put("totalCount", totalCount);
        data.put("avgRating", Math.round(avgRating * 10.0) / 10.0);
        data.put("distribution", distribution);
        return Result.ok(data);
    }

    private String desensitize(String userName) {
        if (userName == null || userName.isBlank()) return "";
        if (userName.contains("@")) {
            int atIdx = userName.indexOf('@');
            if (atIdx <= 2) return userName.substring(0, 1) + "***" + userName.substring(atIdx);
            return userName.substring(0, 2) + "***" + userName.substring(atIdx);
        }
        if (userName.matches("\\d+") && userName.length() >= 7) {
            return userName.substring(0, 3) + "****" + userName.substring(userName.length() - 4);
        }
        if (userName.length() > 2) {
            return userName.substring(0, 1) + "***" + userName.substring(userName.length() - 1);
        }
        return userName;
    }
}
