package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.OrderNoUtil;
import com.mall.common.UserBalanceUtil;
import com.mall.common.enums.OrderStatus;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.OrderService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.util.*;

@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {

    private final MallOrderMapper orderMapper;
    private final MallOrdersGoodsMapper ordersGoodsMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final BalanceLogMapper balanceLogMapper;
    private final ProductMapper productMapper;
    private final ProductSkuMapper skuMapper;
    private final MallCartMapper cartMapper;
    private final MallOrdersPrizeMapper prizeMapper;
    private final SellerGoodsMapper sellerGoodsMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Map<String, Object> createOrder(Long userId, List<Map<String, Object>> items) {
        // Phase 1: Validate SKUs and get server-side prices, calculate total
        BigDecimal total = BigDecimal.ZERO;
        for (Map<String, Object> item : items) {
            String skuId = item.get("skuId").toString();
            ProductSku sku = skuMapper.selectById(skuId);
            if (sku == null)
                throw new BizException("SKU不存在：" + skuId);

            // Validate productId belongs to SKU if provided
            if (item.containsKey("productId") && item.get("productId") != null) {
                String productId = item.get("productId").toString();
                if (!sku.getGoodId().equals(productId))
                    throw new BizException("商品与SKU不匹配");
            }

            // Server-side price: promotionPrice if > 0, else regular price
            BigDecimal price = sku.getPromotionPrice() != null
                && sku.getPromotionPrice().compareTo(BigDecimal.ZERO) > 0
                ? sku.getPromotionPrice() : sku.getPrice();
            if (price == null || price.compareTo(BigDecimal.ZERO) <= 0)
                throw new BizException("SKU价格异常：" + skuId);

            int quantity = Integer.parseInt(item.get("quantity").toString());
            if (quantity <= 0) throw new BizException("购买数量必须大于0");

            total = total.add(price.multiply(BigDecimal.valueOf(quantity)));
            item.put("_serverPrice", price);
        }

        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (balance == null)
            throw new BizException("余额账户不存在");
        BigDecimal available = UserBalanceUtil.getAvailable(balance);
        if (available.compareTo(total) < 0)
            throw new BizException("可用余额不足，请先充值USDT");

        int rows = userBalanceMapper.deductBalance(userId, total, balance.getVersion());
        if (rows == 0) throw new BizException("余额扣减失败，请重试");

        balanceLogMapper.insert(BalanceLog.builder()
            .userId(userId).amount(total.negate())
            .type("ORDER").remark("下单扣款").build());

        String uuid = java.util.UUID.randomUUID().toString().replace("-", "");
        MallOrder order = new MallOrder();
        order.setUuid(uuid);
        order.setOrderNo(OrderNoUtil.generateOrderNo());
        order.setPartyId(userId.toString());
        order.setTotalAmount(total);
        order.setPayAmount(total);
        order.setDiscountAmount(BigDecimal.ZERO);
        order.setOrderStatus(OrderStatus.PENDING.getCode());
        orderMapper.insert(order);

        for (Map<String, Object> item : items) {
            String skuId = item.get("skuId").toString();
            int quantity = Integer.parseInt(item.get("quantity").toString());
            BigDecimal serverPrice = (BigDecimal) item.get("_serverPrice");

            MallOrdersGoods og = new MallOrdersGoods();
            og.setOrderId(order.getUuid());
            og.setGoodsId(item.get("productId").toString());
            og.setSkuId(skuId);
            og.setGoodsNum(quantity);
            og.setGoodsPrize(serverPrice);
            ordersGoodsMapper.insert(og);

            int stockRows = productMapper.deductStock(skuId, quantity);
            if (stockRows == 0) throw new BizException("库存不足：" + skuId);
        }

        cartMapper.delete(new QueryWrapper<MallCart>().eq("user_id", userId)
            .in("sku_id", items.stream().map(i -> i.get("skuId").toString()).toList()));

        Map<String, Object> result = new HashMap<>();
        result.put("orderNo", order.getOrderNo());
        result.put("orderId", order.getUuid());
        result.put("totalAmount", total);
        return result;
    }

    @Override
    public List<Map<String, Object>> list(Long userId, Integer pageNum, Integer pageSize) {
        IPage<MallOrder> page = orderMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<MallOrder>().eq("party_id", userId.toString()).orderByDesc("create_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallOrder o : page.getRecords()) {
            Map<String, Object> item = new HashMap<>();
            item.put("orderNo", o.getOrderNo());
            item.put("totalAmount", o.getTotalAmount());
            item.put("orderStatus", o.getOrderStatus());
            item.put("createTime", o.getCreateTime());
            result.add(item);
        }
        return result;
    }

    @Override
    public Map<String, Object> detail(Long userId, Long orderId) {
        MallOrder order = orderMapper.selectById(orderId.toString());
        if (order == null) throw new BizException("订单不存在");
        if (!order.getPartyId().equals(userId.toString())) throw new BizException("无权查看此订单");
        Map<String, Object> detail = new HashMap<>();
        detail.put("orderNo", order.getOrderNo());
        detail.put("totalAmount", order.getTotalAmount());
        detail.put("payAmount", order.getPayAmount());
        detail.put("orderStatus", order.getOrderStatus());
        detail.put("payStatus", order.getPayStatus());
        detail.put("deliveryStatus", order.getDeliveryStatus());
        detail.put("logisticsNo", order.getLogisticsNo());
        detail.put("createTime", order.getCreateTime());
        List<MallOrdersGoods> goods = ordersGoodsMapper.selectList(
            new QueryWrapper<MallOrdersGoods>().eq("order_id", order.getUuid()));
        detail.put("goods", goods);
        return detail;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void cancel(Long userId, Long orderId) {
        MallOrder order = orderMapper.selectById(orderId.toString());
        if (order == null) throw new BizException("订单不存在");
        if (!order.getPartyId().equals(userId.toString())) throw new BizException("无权操作");
        if (order.getOrderStatus() != OrderStatus.PENDING.getCode()) throw new BizException("订单状态不允许取消");
        order.setOrderStatus(OrderStatus.CANCELLED.getCode());
        orderMapper.updateById(order);

        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", userId));
        if (balance == null) throw new BizException("用户余额不存在");
        int rows = userBalanceMapper.addBalanceWithVersion(userId, order.getPayAmount(), balance.getVersion());
        if (rows == 0) throw new BizException("退款失败，余额版本冲突，请重试");
        balanceLogMapper.insert(BalanceLog.builder()
            .userId(userId).amount(order.getPayAmount())
            .type("REFUND").remark("订单取消退款：" + order.getOrderNo()).build());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void receipt(Long userId, String orderId) {
        MallOrder order = orderMapper.selectById(orderId);
        if (order == null || !order.getPartyId().equals(userId.toString()))
            throw new BizException("订单不存在");
        if (order.getOrderStatus() != OrderStatus.SHIPPED.getCode())
            throw new BizException("该订单状态无法操作");
        order.setOrderStatus(OrderStatus.COMPLETED.getCode());
        orderMapper.updateById(order);
    }

    @Override
    public Map<String, Integer> countStatus(Long userId) {
        List<MallOrder> orders = orderMapper.selectList(
            new QueryWrapper<MallOrder>().eq("party_id", userId.toString()));
        Map<String, Integer> result = new HashMap<>();
        result.put("waitPay", 0);
        result.put("waitDeliver", 0);
        result.put("waitReceipt", 0);
        result.put("completed", 0);
        result.put("refund", 0);
        for (MallOrder o : orders) {
            int s = o.getOrderStatus();
            if (s == OrderStatus.PENDING.getCode()) result.merge("waitPay", 1, Integer::sum);
            else if (s == OrderStatus.PAID.getCode()) result.merge("waitDeliver", 1, Integer::sum);
            else if (s == OrderStatus.SHIPPED.getCode()) result.merge("waitReceipt", 1, Integer::sum);
            else if (s == OrderStatus.COMPLETED.getCode()) result.merge("completed", 1, Integer::sum);
            else if (s == OrderStatus.REFUNDING.getCode()) result.merge("refund", 1, Integer::sum);
        }
        return result;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void refund(Long userId, Long orderId, String reason) {
        MallOrder order = orderMapper.selectById(orderId.toString());
        if (order == null) throw new BizException("订单不存在");
        if (!order.getPartyId().equals(userId.toString())) throw new BizException("无权操作");
        int status = order.getOrderStatus();
        if (status != OrderStatus.PAID.getCode() && status != OrderStatus.SHIPPED.getCode()
            && status != OrderStatus.COMPLETED.getCode())
            throw new BizException("订单状态不允许退款");
        order.setOrderStatus(OrderStatus.REFUNDING.getCode());
        orderMapper.updateById(order);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void refundApply(Long userId, String orderId, String returnReason,
                            BigDecimal money, String returnDetail) {
        MallOrder order = orderMapper.selectById(orderId);
        if (order == null) throw new BizException("订单不存在");
        if (!order.getPartyId().equals(userId.toString())) throw new BizException("无权操作");
        int status = order.getOrderStatus();
        if (status != OrderStatus.PAID.getCode() && status != OrderStatus.SHIPPED.getCode()
            && status != OrderStatus.COMPLETED.getCode())
            throw new BizException("当前订单状态不支持退款");

        order.setOrderStatus(OrderStatus.REFUNDING.getCode());
        orderMapper.updateById(order);

        MallOrdersPrize prize = new MallOrdersPrize();
        prize.setUuid(java.util.UUID.randomUUID().toString().replace("-", ""));
        prize.setPartyId(userId.toString());
        prize.setUserCode(order.getOrderNo());
        prize.setReturnReason(returnReason);
        prize.setReturnDetail(returnDetail);
        prize.setReturnStatus(1);
        prize.setRefundTime(java.time.LocalDateTime.now());
        prize.setPrizeOriginal(money.doubleValue());
        prize.setPrizeReal(money.doubleValue());
        prizeMapper.insert(prize);
    }

    @Override
    public List<Map<String, Object>> listAll(Integer pageNum, Integer pageSize) {
        IPage<MallOrder> page = orderMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<MallOrder>().orderByDesc("create_time"));
        List<Map<String, Object>> result = new ArrayList<>();
        for (MallOrder o : page.getRecords()) {
            Map<String, Object> item = new HashMap<>();
            item.put("orderNo", o.getOrderNo());
            item.put("partyId", o.getPartyId());
            item.put("totalAmount", o.getTotalAmount());
            item.put("payAmount", o.getPayAmount());
            item.put("orderStatus", o.getOrderStatus());
            item.put("payStatus", o.getPayStatus());
            item.put("deliveryStatus", o.getDeliveryStatus());
            item.put("createTime", o.getCreateTime());
            result.add(item);
        }
        return result;
    }

    @Override
    @Transactional
    public List<Map<String, Object>> saveGoodsBuy(Long userId, String goodsUuid, int num) {
        SellerGoods sellerGoods = sellerGoodsMapper.selectById(goodsUuid);
        if (sellerGoods == null || sellerGoods.getStatus() != 1)
            throw new BizException("商品不存在或已下架");
        if (num <= 0) throw new BizException("购买数量必须大于0");
        if (sellerGoods.getStock() != null && sellerGoods.getStock() < num)
            throw new BizException("库存不足");

        BigDecimal unitPrice = sellerGoods.getPrice();
        if (unitPrice == null || unitPrice.compareTo(BigDecimal.ZERO) <= 0)
            throw new BizException("商品价格异常");

        BigDecimal total = unitPrice.multiply(BigDecimal.valueOf(num));
        String uuid = UUID.randomUUID().toString().replace("-", "");

        MallOrder order = new MallOrder();
        order.setUuid(uuid);
        order.setOrderNo(OrderNoUtil.generateOrderNo());
        order.setPartyId(userId.toString());
        order.setTotalAmount(total);
        order.setPayAmount(total);
        order.setDiscountAmount(BigDecimal.ZERO);
        order.setOrderStatus(OrderStatus.PENDING.getCode());
        orderMapper.insert(order);

        MallOrdersGoods og = new MallOrdersGoods();
        og.setOrderId(uuid);
        og.setGoodsId(goodsUuid);
        og.setGoodsNum(num);
        og.setGoodsPrize(unitPrice);
        ordersGoodsMapper.insert(og);

        Map<String, Object> item = new HashMap<>();
        item.put("orderId", uuid);
        item.put("orderNo", order.getOrderNo());
        item.put("totalAmount", total);
        item.put("goodsName", sellerGoods.getGoodsName());
        return Collections.singletonList(item);
    }

}
