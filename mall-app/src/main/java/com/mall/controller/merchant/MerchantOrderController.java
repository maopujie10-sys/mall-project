package com.mall.controller.merchant;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.Result;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.MerchantService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 商家端-订单管理（迁移自旧商城 SellerOrdersController）
 * 含高级筛选/退货退款详情/退货列表/未采购统计等原 MerchantController 未覆盖功能
 */
@RestController
@RequestMapping("/merchant")
@RequiredArgsConstructor
public class MerchantOrderController {

    private final MallOrdersPrizeMapper ordersPrizeMapper;
    private final MallOrdersGoodsMapper ordersGoodsMapper;
    private final MallOrderMapper orderMapper;
    private final MallOrderLogMapper orderLogMapper;
    private final UserMapper userMapper;
    private final MerchantMapper merchantMapper;
    private final MerchantService merchantService;

    /**
     * 商家订单高级列表（含日期范围、采购状态、支付状态筛选）
     */
    @GetMapping("/my-orders/advanced")
    public Result<?> advancedOrderList(@RequestAttribute Long userId,
                                       @RequestParam(defaultValue = "1") Integer pageNum,
                                       @RequestParam(defaultValue = "10") Integer pageSize,
                                       @RequestParam(required = false) String status,
                                       @RequestParam(required = false) String orderId,
                                       @RequestParam(required = false) Integer payStatus,
                                       @RequestParam(required = false) Integer purchStatus,
                                       @RequestParam(required = false) String begin,
                                       @RequestParam(required = false) String end) {

        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        QueryWrapper<MallOrdersPrize> qw = new QueryWrapper<>();
        qw.eq("seller_id", String.valueOf(merchant.getUserId()));
        if (orderId != null && !orderId.isBlank()) qw.eq("id", orderId);
        if (payStatus != null && payStatus != -1) qw.eq("pay_status", payStatus);
        if (purchStatus != null) qw.eq("purch_status", purchStatus);
        if (status != null && !status.isBlank()) qw.eq("status", Integer.valueOf(status));
        if (begin != null && !begin.isBlank()) qw.ge("create_time", begin + " 00:00:00");
        if (end != null && !end.isBlank()) qw.le("create_time", end + " 23:59:59");
        qw.orderByDesc("create_time");

        Page<MallOrdersPrize> page = new Page<>(pageNum, pageSize);
        Page<MallOrdersPrize> result = ordersPrizeMapper.selectPage(page, qw);

        List<Map<String, Object>> list = result.getRecords().stream().map(order -> {
            Map<String, Object> m = new HashMap<>();
            m.put("id", order.getUuid());
            m.put("contacts", order.getContacts());
            m.put("prizeReal", order.getPrizeReal());
            m.put("profit", order.getProfit());
            m.put("purchStatus", order.getPurchStatus());
            m.put("payStatus", payStatus != null && payStatus == -1 ? order.getStatus() : order.getPayStatus());
            m.put("status", order.getStatus());
            m.put("createTime", order.getCreateTime());
            m.put("purchTime", order.getPurchTime() != null ? order.getPurchTime().toString() : "");
            m.put("partyId", order.getPartyId());

            // totalCost = sum(goodsNum * systemPrice)
            QueryWrapper<MallOrdersGoods> goodsQw = new QueryWrapper<>();
            goodsQw.eq("order_id", order.getUuid());
            List<MallOrdersGoods> goodsList = ordersGoodsMapper.selectList(goodsQw);
            double totalCost = goodsList.stream()
                    .mapToDouble(g -> g.getGoodsNum() * g.getSystemPrice().doubleValue()).sum();
            m.put("totalCost", totalCost);

            if (order.getPartyId() != null) {
                try {
                    User user = userMapper.selectById(Long.valueOf(order.getPartyId()));
                    m.put("username", user != null ? user.getPhone() : "");
                } catch (NumberFormatException e) {
                    m.put("username", "");
                }
            } else {
                m.put("username", "");
            }

            return m;
        }).collect(Collectors.toList());

        Map<String, Object> data = new HashMap<>();
        data.put("pageInfo", Map.of("pageNum", pageNum, "pageSize", pageSize, "totalElements", result.getTotal()));
        data.put("pageList", list);
        return Result.ok(data);
    }

    /**
     * 订单详情（商家视角，含采购金额/物流/地址等完整信息）
     */
    @GetMapping("/my-orders/{id}")
    public Result<?> orderDetail(@RequestAttribute Long userId, @PathVariable String id) {
        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        MallOrdersPrize order = ordersPrizeMapper.selectById(id);
        if (order == null) return Result.fail("订单不存在");
        if (!String.valueOf(merchant.getUserId()).equals(order.getSellerId())) {
            return Result.fail("商家只允许查看自己的订单");
        }

        Map<String, Object> detail = new HashMap<>();
        detail.put("id", order.getUuid());
        detail.put("createTime", order.getCreateTime());
        detail.put("purchTime", order.getPurchTime());
        detail.put("status", order.getPayStatus());
        detail.put("systemPrice", order.getSystemPrice());
        detail.put("prizeReal", order.getPrizeReal());
        detail.put("address", order.getAddress());
        detail.put("contacts", order.getContacts());
        detail.put("email", order.getEmail());
        detail.put("phone", order.getPhone());
        detail.put("country", order.getCountry());
        detail.put("province", order.getProvince());
        detail.put("city", order.getCity());
        detail.put("postcode", order.getPostcode());
        detail.put("partyId", order.getPartyId());
        detail.put("returnStatus", order.getReturnStatus());
        detail.put("returnReason", order.getReturnReason());
        detail.put("returnDetail", order.getReturnDetail());
        detail.put("profit", order.getProfit());
        detail.put("fees", order.getFees());
        detail.put("tax", order.getTax());

        double returnPrice = (order.getFees() != null ? order.getFees() : 0)
                + (order.getTax() != null ? order.getTax() : 0)
                + (order.getPrizeReal() != null ? order.getPrizeReal() : 0);
        detail.put("returnPrice", returnPrice);

        if (order.getPartyId() != null) {
            try {
                User user = userMapper.selectById(Long.valueOf(order.getPartyId()));
                detail.put("username", user != null ? user.getPhone() : "");
            } catch (NumberFormatException e) {
                detail.put("username", "");
            }
        } else {
            detail.put("username", "");
        }

        // Order goods items
        QueryWrapper<MallOrdersGoods> goodsQw = new QueryWrapper<>();
        goodsQw.eq("order_id", order.getUuid());
        List<MallOrdersGoods> goodsList = ordersGoodsMapper.selectList(goodsQw);
        List<Map<String, Object>> items = goodsList.stream().map(g -> {
            Map<String, Object> gm = new HashMap<>();
            gm.put("goodsId", g.getGoodsId());
            gm.put("goodsNum", g.getGoodsNum());
            gm.put("systemPrice", g.getSystemPrice());
            gm.put("goodsPrize", g.getGoodsPrize());
            gm.put("goodsReal", g.getGoodsReal());
            gm.put("skuId", g.getSkuId());
            return gm;
        }).collect(Collectors.toList());
        detail.put("goods", items);

        return Result.ok(detail);
    }

    /**
     * 退货退款列表
     */
    @GetMapping("/my-orders/returns")
    public Result<?> returnList(@RequestAttribute Long userId,
                                @RequestParam(defaultValue = "1") Integer pageNum,
                                @RequestParam(defaultValue = "10") Integer pageSize,
                                @RequestParam(required = false) Integer returnStatus,
                                @RequestParam(required = false) String begin,
                                @RequestParam(required = false) String end) {

        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        QueryWrapper<MallOrdersPrize> qw = new QueryWrapper<>();
        qw.eq("seller_id", String.valueOf(merchant.getUserId()));
        qw.gt("return_status", 0);
        if (returnStatus != null) qw.eq("return_status", returnStatus);
        if (begin != null && !begin.isBlank()) qw.ge("create_time", begin + " 00:00:00");
        if (end != null && !end.isBlank()) qw.le("create_time", end + " 23:59:59");
        qw.orderByDesc("create_time");

        Page<MallOrdersPrize> page = new Page<>(pageNum, pageSize);
        Page<MallOrdersPrize> result = ordersPrizeMapper.selectPage(page, qw);

        List<Map<String, Object>> list = result.getRecords().stream().map(order -> {
            Map<String, Object> m = new HashMap<>();
            m.put("refundTime", order.getRefundTime());
            m.put("id", order.getUuid());
            m.put("createTime", order.getCreateTime());
            double retPrice = (order.getFees() != null ? order.getFees() : 0)
                    + (order.getTax() != null ? order.getTax() : 0)
                    + (order.getPrizeReal() != null ? order.getPrizeReal() : 0);
            m.put("returnPrice", retPrice);
            m.put("returnStatus", order.getReturnStatus());
            m.put("returnReason", order.getReturnReason());
            m.put("returnDetail", order.getReturnDetail());
            m.put("partyId", order.getPartyId());
            if (order.getPartyId() != null) {
                try {
                    User user = userMapper.selectById(Long.valueOf(order.getPartyId()));
                    m.put("username", user != null ? user.getPhone() : "");
                } catch (NumberFormatException e) {
                    m.put("username", "");
                }
            } else {
                m.put("username", "");
            }
            return m;
        }).collect(Collectors.toList());

        Map<String, Object> data = new HashMap<>();
        data.put("pageInfo", Map.of("pageNum", pageNum, "pageSize", pageSize, "totalElements", result.getTotal()));
        data.put("pageList", list);
        return Result.ok(data);
    }

    /**
     * 退货退款详情
     */
    @GetMapping("/my-orders/{id}/return-detail")
    public Result<?> returnDetail(@RequestAttribute Long userId, @PathVariable String id) {
        MallOrdersPrize order = ordersPrizeMapper.selectById(id);
        if (order == null) return Result.fail("订单不存在");

        Map<String, Object> detail = new HashMap<>();
        detail.put("refundTime", order.getRefundTime());
        detail.put("id", order.getUuid());
        double retPrice = (order.getFees() != null ? order.getFees() : 0)
                + (order.getTax() != null ? order.getTax() : 0)
                + (order.getPrizeReal() != null ? order.getPrizeReal() : 0);
        detail.put("returnPrice", retPrice);
        detail.put("returnStatus", order.getReturnStatus());
        detail.put("returnReason", order.getReturnReason());
        detail.put("returnDetail", order.getReturnDetail());
        detail.put("partyId", order.getPartyId());

        if (order.getPartyId() != null) {
            try {
                User user = userMapper.selectById(Long.valueOf(order.getPartyId()));
                detail.put("username", user != null ? user.getPhone() : "");
            } catch (NumberFormatException e) {
                detail.put("username", "");
            }
        } else {
            detail.put("username", "");
        }

        return Result.ok(detail);
    }

    /**
     * 统计未采购订单数量
     */
    @GetMapping("/my-orders/unpushed-count")
    public Result<?> unpushedCount(@RequestAttribute Long userId) {
        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        QueryWrapper<MallOrdersPrize> qw = new QueryWrapper<>();
        qw.eq("seller_id", String.valueOf(merchant.getUserId()));
        qw.eq("purch_status", 0);
        qw.eq("status", 2);
        Long count = ordersPrizeMapper.selectCount(qw);

        return Result.ok(Map.of("noPushNum", count));
    }
}
