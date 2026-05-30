package com.mall.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.common.JwtUtil;
import com.mall.common.OrderNoUtil;
import com.mall.common.UserBalanceUtil;
import com.mall.common.enums.OrderStatus;
import com.mall.common.exception.BizException;
import com.mall.entity.*;
import com.mall.mapper.*;
import com.mall.service.IdcodeService;
import com.mall.service.MerchantService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class MerchantServiceImpl implements MerchantService {

    private final MerchantMapper merchantMapper;
    private final UserMapper userMapper;
    private final MallOrderMapper orderMapper;
    private final MallOrdersGoodsMapper ordersGoodsMapper;
    private final ProductMapper productMapper;
    private final ProductSkuMapper skuMapper;
    private final ProductImageMapper productImageMapper;
    private final ProductReviewMapper reviewMapper;
    private final UserBalanceMapper userBalanceMapper;
    private final BalanceLogMapper balanceLogMapper;
    private final RechargeOrderMapper rechargeOrderMapper;
    private final WithdrawOrderMapper withdrawOrderMapper;
    private final ChatMessageMapper chatMessageMapper;
    private final MerchantApplyMapper merchantApplyMapper;
    private final SystemGoodsMapper systemGoodsMapper;
    private final MallComboRecordMapper comboRecordMapper;
    private final IdcodeService idcodeService;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    // ==================== Auth ====================

    @Override
    public Map<String, Object> loginByUsername(String username, String password) {
        User user = userMapper.selectOne(new QueryWrapper<User>().eq("phone", username));
        if (user == null) throw new BizException("账号或密码错误");
        if (!passwordEncoder.matches(password, user.getPassword()))
            throw new BizException("账号或密码错误");
        if (user.getStatus() != null && user.getStatus() != 0)
            throw new BizException("账号已被禁用");

        Merchant merchant = merchantMapper.selectOne(
            new QueryWrapper<Merchant>().eq("user_id", user.getId()).eq("status", 1));
        if (merchant == null) throw new BizException("该账号未开通商家权限");

        String token = jwtUtil.generateToken(merchant.getId(), "MERCHANT");
        Map<String, Object> info = new HashMap<>();
        info.put("id", merchant.getId());
        info.put("userId", merchant.getUserId());
        info.put("shopName", merchant.getShopName());
        info.put("shopPhone", merchant.getShopPhone());
        info.put("shopAddress", merchant.getShopAddress());
        info.put("avatar", merchant.getAvatar());
        info.put("contact", merchant.getContact());
        info.put("status", merchant.getStatus());
        return Map.of("token", token, "info", info);
    }

    @Override
    public void changePassword(Long merchantId, String oldPassword, String newPassword) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");
        User user = userMapper.selectById(merchant.getUserId());
        if (user == null) throw new BizException("用户不存在");
        if (!passwordEncoder.matches(oldPassword, user.getPassword()))
            throw new BizException("原密码错误");
        if (newPassword == null || newPassword.length() < 6)
            throw new BizException("新密码不能少于6位");
        user.setPassword(passwordEncoder.encode(newPassword));
        userMapper.updateById(user);
    }

    @Override
    public void resetPasswordSendCode(String phone, String ip) {
        User user = userMapper.selectOne(new QueryWrapper<User>().eq("phone", phone).eq("deleted", 0));
        if (user == null) throw new BizException("该手机号未注册");
        if (user.getStatus() != null && user.getStatus() != 0) throw new BizException("账号已被禁用");
        Merchant merchant = merchantMapper.selectOne(
            new QueryWrapper<Merchant>().eq("user_id", user.getId()).eq("status", 1));
        if (merchant == null) throw new BizException("该账号未开通商家权限");
        idcodeService.send(phone, "MERCHANT_RESET_PWD", ip);
    }

    @Override
    @Transactional
    public void resetPassword(String phone, String code, String newPassword) {
        if (newPassword == null || newPassword.length() < 6) throw new BizException("密码至少6位");
        boolean ok = idcodeService.verify(phone, code, "MERCHANT_RESET_PWD");
        if (!ok) throw new BizException("验证码校验失败");
        User user = userMapper.selectOne(new QueryWrapper<User>().eq("phone", phone).eq("deleted", 0));
        if (user == null) throw new BizException("用户不存在");
        Merchant merchant = merchantMapper.selectOne(
            new QueryWrapper<Merchant>().eq("user_id", user.getId()).eq("status", 1));
        if (merchant == null) throw new BizException("该账号未开通商家权限");
        userMapper.update(null, new UpdateWrapper<User>().eq("id", user.getId())
                .set("password", passwordEncoder.encode(newPassword)));
    }

    // ==================== Dashboard ====================

    @Override
    public Map<String, Object> dashboard(Long merchantId) {
        Map<String, Object> result = new HashMap<>();

        String merchantIdStr = merchantId.toString();

        long productCount = productMapper.selectCount(
            new QueryWrapper<Product>().eq("merchant_id", merchantId));

        List<Product> products = productMapper.selectList(
            new QueryWrapper<Product>().eq("merchant_id", merchantId));
        List<String> productIds = products.stream().map(p -> p.getId().toString()).toList();

        long totalOrders = 0;
        long pendingOrders = 0;
        BigDecimal totalRevenue = BigDecimal.ZERO;

        if (!productIds.isEmpty()) {
            List<MallOrdersGoods> orderGoods = ordersGoodsMapper.selectList(
                new QueryWrapper<MallOrdersGoods>().in("goods_id", productIds));
            Set<String> orderIds = orderGoods.stream()
                .map(MallOrdersGoods::getOrderId).collect(Collectors.toSet());

            if (!orderIds.isEmpty()) {
                List<MallOrder> orders = orderMapper.selectBatchIds(orderIds);
                totalOrders = orders.size();
                pendingOrders = orders.stream().filter(o -> o.getOrderStatus() != null && o.getOrderStatus() == 0).count();
                totalRevenue = orders.stream()
                    .filter(o -> o.getOrderStatus() != null && o.getOrderStatus() != 4)
                    .map(MallOrder::getPayAmount)
                    .filter(Objects::nonNull)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);
            }
        }

        String today = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        long todayOrders = 0;
        if (!productIds.isEmpty()) {
            List<MallOrdersGoods> todayGoods = ordersGoodsMapper.selectList(
                new QueryWrapper<MallOrdersGoods>().in("goods_id", productIds));
            Set<String> todayOrderIds = todayGoods.stream()
                .map(MallOrdersGoods::getOrderId).collect(Collectors.toSet());
            if (!todayOrderIds.isEmpty()) {
                todayOrders = orderMapper.selectCount(
                    new QueryWrapper<MallOrder>().in("uuid", todayOrderIds)
                        .ge("create_time", today + " 00:00:00"));
            }
        }

        long reviewCount = 0;
        if (!productIds.isEmpty()) {
            reviewCount = reviewMapper.selectCount(
                new QueryWrapper<ProductReview>().in("system_goods_id", productIds));
        }

        result.put("productCount", productCount);
        result.put("totalOrders", totalOrders);
        result.put("pendingOrders", pendingOrders);
        result.put("todayOrders", todayOrders);
        result.put("totalRevenue", totalRevenue);
        result.put("reviewCount", reviewCount);

        List<Map<String, Object>> topProducts = new ArrayList<>();
        List<Product> sortedProducts = new ArrayList<>(products);
        sortedProducts.sort((a, b) -> Integer.compare(
            b.getSales() != null ? b.getSales() : 0,
            a.getSales() != null ? a.getSales() : 0));
        for (int i = 0; i < Math.min(5, sortedProducts.size()); i++) {
            Product p = sortedProducts.get(i);
            topProducts.add(Map.of("id", p.getId(), "name", p.getName(),
                "sales", p.getSales() != null ? p.getSales() : 0,
                "price", p.getPrice()));
        }
        result.put("topProducts", topProducts);
        return result;
    }

    // ==================== Info & Store ====================

    @Override
    public Object getInfo(Long merchantId) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");
        Map<String, Object> info = new HashMap<>();
        info.put("id", merchant.getId());
        info.put("userId", merchant.getUserId());
        info.put("shopName", merchant.getShopName());
        info.put("shopPhone", merchant.getShopPhone());
        info.put("shopAddress", merchant.getShopAddress());
        info.put("shopRemark", merchant.getShopRemark());
        info.put("avatar", merchant.getAvatar());
        info.put("banner1", merchant.getBanner1());
        info.put("banner2", merchant.getBanner2());
        info.put("banner3", merchant.getBanner3());
        info.put("contact", merchant.getContact());
        info.put("status", merchant.getStatus());
        info.put("createTime", merchant.getCreateTime());
        return info;
    }

    @Override
    public void updateShopInfo(Long merchantId, Map<String, Object> data) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");
        if (data.containsKey("shopName")) merchant.setShopName(data.get("shopName").toString());
        if (data.containsKey("shopPhone")) merchant.setShopPhone(data.get("shopPhone").toString());
        if (data.containsKey("shopAddress")) merchant.setShopAddress(data.get("shopAddress").toString());
        if (data.containsKey("shopRemark")) merchant.setShopRemark(data.get("shopRemark").toString());
        if (data.containsKey("avatar")) merchant.setAvatar(data.get("avatar").toString());
        if (data.containsKey("banner1")) merchant.setBanner1(data.get("banner1").toString());
        if (data.containsKey("banner2")) merchant.setBanner2(data.get("banner2").toString());
        if (data.containsKey("banner3")) merchant.setBanner3(data.get("banner3").toString());
        if (data.containsKey("contact")) merchant.setContact(data.get("contact").toString());
        merchantMapper.updateById(merchant);
    }

    // ==================== Product CRUD ====================

    @Override
    public Map<String, Object> productList(Long merchantId, Integer pageNum, Integer pageSize,
                                            String keyword, Integer status) {
        QueryWrapper<Product> qw = new QueryWrapper<Product>()
            .eq("merchant_id", merchantId)
            .orderByDesc("create_time");
        if (keyword != null && !keyword.isBlank()) {
            qw.like("name", keyword);
        }
        if (status != null) {
            qw.eq("status", status);
        }
        IPage<Product> page = productMapper.selectPage(new Page<>(pageNum, pageSize), qw);
        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("list", page.getRecords());
        return result;
    }

    @Override
    public Map<String, Object> productDetail(Long merchantId, Long productId) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        if (!merchantId.equals(product.getMerchantId())) throw new BizException("无权查看此商品");

        List<ProductSku> skus = skuMapper.selectList(
            new QueryWrapper<ProductSku>().eq("good_id", productId.toString()));

        Map<String, Object> detail = new HashMap<>();
        detail.put("id", product.getId());
        detail.put("name", product.getName());
        detail.put("categoryId", product.getCategoryId());
        detail.put("brandId", product.getBrandId());
        detail.put("subtitle", product.getSubtitle());
        detail.put("mainImage", product.getMainImage());
        detail.put("detailImages", product.getDetailImages());
        detail.put("price", product.getPrice());
        detail.put("originalPrice", product.getOriginalPrice());
        detail.put("costPrice", product.getCostPrice());
        detail.put("totalStock", product.getTotalStock());
        detail.put("sales", product.getSales());
        detail.put("status", product.getStatus());
        detail.put("isHot", product.getIsHot());
        detail.put("isNew", product.getIsNew());
        detail.put("sort", product.getSort());
        detail.put("description", product.getDescription());
        detail.put("unit", product.getUnit());
        detail.put("isWholesale", product.getIsWholesale());
        detail.put("createTime", product.getCreateTime());
        detail.put("skus", skus);
        return detail;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void productAdd(Long merchantId, Map<String, Object> data) {
        Product product = new Product();
        product.setMerchantId(merchantId);
        product.setName(data.get("name").toString());
        product.setCategoryId(Long.valueOf(data.get("categoryId").toString()));
        if (data.containsKey("subtitle")) product.setSubtitle(data.get("subtitle").toString());
        if (data.containsKey("mainImage")) product.setMainImage(data.get("mainImage").toString());
        if (data.containsKey("detailImages")) product.setDetailImages(data.get("detailImages").toString());
        if (data.containsKey("price")) product.setPrice(new BigDecimal(data.get("price").toString()));
        if (data.containsKey("originalPrice")) product.setOriginalPrice(new BigDecimal(data.get("originalPrice").toString()));
        if (data.containsKey("costPrice")) product.setCostPrice(new BigDecimal(data.get("costPrice").toString()));
        if (data.containsKey("totalStock")) product.setTotalStock(Integer.parseInt(data.get("totalStock").toString()));
        if (data.containsKey("description")) product.setDescription(data.get("description").toString());
        if (data.containsKey("unit")) product.setUnit(data.get("unit").toString());
        product.setStatus(1);
        product.setSales(0);
        product.setVirtualSales(0);
        product.setVirtualViews(0);
        productMapper.insert(product);

        if (data.containsKey("skus") && data.get("skus") instanceof List) {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> skus = (List<Map<String, Object>>) data.get("skus");
            for (Map<String, Object> skuData : skus) {
                ProductSku sku = new ProductSku();
                sku.setId(UUID.randomUUID().toString().replace("-", ""));
                sku.setGoodId(product.getId().toString());
                if (skuData.containsKey("price"))
                    sku.setPrice(new BigDecimal(skuData.get("price").toString()));
                if (skuData.containsKey("sale"))
                    sku.setSale(Integer.parseInt(skuData.get("sale").toString()));
                if (skuData.containsKey("spData"))
                    sku.setSpData(skuData.get("spData").toString());
                if (skuData.containsKey("pic"))
                    sku.setPic(skuData.get("pic").toString());
                skuMapper.insert(sku);
            }
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void productUpdate(Long merchantId, Long productId, Map<String, Object> data) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        if (!merchantId.equals(product.getMerchantId())) throw new BizException("无权操作此商品");

        if (data.containsKey("name")) product.setName(data.get("name").toString());
        if (data.containsKey("categoryId")) product.setCategoryId(Long.valueOf(data.get("categoryId").toString()));
        if (data.containsKey("subtitle")) product.setSubtitle(data.get("subtitle").toString());
        if (data.containsKey("mainImage")) product.setMainImage(data.get("mainImage").toString());
        if (data.containsKey("detailImages")) product.setDetailImages(data.get("detailImages").toString());
        if (data.containsKey("price")) product.setPrice(new BigDecimal(data.get("price").toString()));
        if (data.containsKey("originalPrice")) product.setOriginalPrice(new BigDecimal(data.get("originalPrice").toString()));
        if (data.containsKey("costPrice")) product.setCostPrice(new BigDecimal(data.get("costPrice").toString()));
        if (data.containsKey("totalStock")) product.setTotalStock(Integer.parseInt(data.get("totalStock").toString()));
        if (data.containsKey("description")) product.setDescription(data.get("description").toString());
        if (data.containsKey("unit")) product.setUnit(data.get("unit").toString());
        productMapper.updateById(product);
    }

    @Override
    public void productDelete(Long merchantId, Long productId) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        if (!merchantId.equals(product.getMerchantId())) throw new BizException("无权操作此商品");
        productMapper.deleteById(productId);
    }

    @Override
    public void productUpdateStatus(Long merchantId, Long productId, Integer status) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        if (!merchantId.equals(product.getMerchantId())) throw new BizException("无权操作此商品");
        product.setStatus(status);
        productMapper.updateById(product);
    }

    // ==================== Orders ====================

    @Override
    public Map<String, Object> orderList(Long merchantId, Integer pageNum, Integer pageSize, Integer status) {
        List<Product> products = productMapper.selectList(
            new QueryWrapper<Product>().eq("merchant_id", merchantId));
        if (products.isEmpty()) {
            return Map.of("total", 0L, "list", List.of());
        }
        List<String> productIds = products.stream().map(p -> p.getId().toString()).toList();

        List<MallOrdersGoods> allGoods = ordersGoodsMapper.selectList(
            new QueryWrapper<MallOrdersGoods>().in("goods_id", productIds));
        Set<String> orderIds = allGoods.stream()
            .map(MallOrdersGoods::getOrderId).collect(Collectors.toSet());
        if (orderIds.isEmpty()) {
            return Map.of("total", 0L, "list", List.of());
        }

        QueryWrapper<MallOrder> qw = new QueryWrapper<MallOrder>()
            .in("uuid", orderIds).orderByDesc("create_time");
        if (status != null) {
            qw.eq("order_status", status);
        }

        List<MallOrder> allMatching = orderMapper.selectList(qw);
        long total = allMatching.size();
        int start = (pageNum - 1) * pageSize;
        int end = Math.min(start + pageSize, allMatching.size());
        List<MallOrder> page = start < allMatching.size() ? allMatching.subList(start, end) : List.of();

        List<Map<String, Object>> list = new ArrayList<>();
        for (MallOrder o : page) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", o.getUuid());
            item.put("orderNo", o.getOrderNo());
            item.put("totalAmount", o.getTotalAmount());
            item.put("payAmount", o.getPayAmount());
            item.put("orderStatus", o.getOrderStatus());
            item.put("status", o.getOrderStatus());
            item.put("payStatus", o.getPayStatus());
            item.put("deliveryStatus", o.getDeliveryStatus());
            item.put("logisticsCompany", o.getLogisticsCompany());
            item.put("logisticsNo", o.getLogisticsNo());
            item.put("buyerName", o.getReceiverName());
            item.put("createTime", o.getCreateTime());
            list.add(item);
        }
        return Map.of("total", total, "list", list);
    }

    @Override
    public Map<String, Object> orderDetail(Long merchantId, String orderId) {
        MallOrder order = orderMapper.selectById(orderId);
        if (order == null) throw new BizException("订单不存在");

        List<MallOrdersGoods> goods = ordersGoodsMapper.selectList(
            new QueryWrapper<MallOrdersGoods>().eq("order_id", order.getUuid()));
        List<String> goodIds = goods.stream().map(MallOrdersGoods::getGoodsId).toList();
        List<Product> orderProducts = goodIds.isEmpty() ? List.of() :
            productMapper.selectBatchIds(goodIds.stream().map(Long::valueOf).toList());

        boolean ownsProduct = orderProducts.stream()
            .anyMatch(p -> merchantId.equals(p.getMerchantId()));
        if (!ownsProduct) throw new BizException("无权查看此订单");

        Map<String, Product> productMap = orderProducts.stream()
            .collect(Collectors.toMap(p -> p.getId().toString(), p -> p, (a, b) -> a));

        List<Map<String, Object>> items = new ArrayList<>();
        for (MallOrdersGoods g : goods) {
            Product p = productMap.get(g.getGoodsId());
            Map<String, Object> gi = new HashMap<>();
            gi.put("productName", p != null ? p.getName() : "");
            gi.put("image", p != null ? p.getMainImage() : "");
            gi.put("price", g.getGoodsPrize());
            gi.put("quantity", g.getGoodsNum());
            items.add(gi);
        }

        Map<String, Object> detail = new HashMap<>();
        detail.put("id", order.getUuid());
        detail.put("orderNo", order.getOrderNo());
        detail.put("totalAmount", order.getTotalAmount());
        detail.put("payAmount", order.getPayAmount());
        detail.put("discountAmount", order.getDiscountAmount());
        detail.put("orderStatus", order.getOrderStatus());
        detail.put("status", order.getOrderStatus());
        detail.put("payStatus", order.getPayStatus());
        detail.put("deliveryStatus", order.getDeliveryStatus());
        detail.put("logisticsCompany", order.getLogisticsCompany());
        detail.put("company", order.getLogisticsCompany());
        detail.put("logisticsNo", order.getLogisticsNo());
        detail.put("trackingNo", order.getLogisticsNo());
        detail.put("buyerName", order.getReceiverName());
        detail.put("address", order.getReceiverAddress());
        detail.put("remark", order.getRemark());
        detail.put("payTime", order.getPayTime());
        detail.put("deliveryTime", order.getDeliveryTime());
        detail.put("finishTime", order.getFinishTime());
        detail.put("createTime", order.getCreateTime());
        detail.put("items", items);
        detail.put("goods", goods);
        return detail;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void shipOrder(Long merchantId, String orderId, String company, String trackingNo) {
        MallOrder order = orderMapper.selectById(orderId);
        if (order == null) throw new BizException("订单不存在");

        List<MallOrdersGoods> goods = ordersGoodsMapper.selectList(
            new QueryWrapper<MallOrdersGoods>().eq("order_id", order.getUuid()));
        List<String> goodIds = goods.stream().map(MallOrdersGoods::getGoodsId).toList();
        List<Product> orderProducts = goodIds.isEmpty() ? List.of() :
            productMapper.selectBatchIds(goodIds.stream().map(Long::valueOf).toList());
        boolean ownsProduct = orderProducts.stream()
            .anyMatch(p -> merchantId.equals(p.getMerchantId()));
        if (!ownsProduct) throw new BizException("无权操作此订单");

        if (order.getOrderStatus() != OrderStatus.PENDING.getCode()) throw new BizException("订单状态不允许发货");
        order.setOrderStatus(OrderStatus.SHIPPED.getCode());
        order.setLogisticsCompany(company);
        order.setLogisticsNo(trackingNo);
        order.setDeliveryTime(LocalDateTime.now());
        orderMapper.updateById(order);
    }

    // ==================== Reviews ====================

    @Override
    public Map<String, Object> reviewList(Long merchantId, Integer pageNum, Integer pageSize) {
        List<Product> products = productMapper.selectList(
            new QueryWrapper<Product>().eq("merchant_id", merchantId));
        if (products.isEmpty()) return Map.of("total", 0L, "list", List.of());

        List<String> productIds = products.stream().map(p -> p.getId().toString()).toList();
        IPage<ProductReview> page = reviewMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<ProductReview>().in("system_goods_id", productIds).orderByDesc("evaluation_time"));
        return Map.of("total", page.getTotal(), "list", page.getRecords());
    }

    // ==================== Refund ====================

    @Override
    public Map<String, Object> refundList(Long merchantId, Integer pageNum, Integer pageSize) {
        List<Product> products = productMapper.selectList(
            new QueryWrapper<Product>().eq("merchant_id", merchantId));
        if (products.isEmpty()) return Map.of("total", 0L, "list", List.of());

        List<String> productIds = products.stream().map(p -> p.getId().toString()).toList();
        List<MallOrdersGoods> allGoods = ordersGoodsMapper.selectList(
            new QueryWrapper<MallOrdersGoods>().in("goods_id", productIds));
        Set<String> orderIds = allGoods.stream()
            .map(MallOrdersGoods::getOrderId).collect(Collectors.toSet());
        if (orderIds.isEmpty()) return Map.of("total", 0L, "list", List.of());

        QueryWrapper<MallOrder> qw = new QueryWrapper<MallOrder>()
            .in("uuid", orderIds).eq("order_status", 5).orderByDesc("create_time");
        List<MallOrder> allMatching = orderMapper.selectList(qw);
        long total = allMatching.size();
        int start = (pageNum - 1) * pageSize;
        int end = Math.min(start + pageSize, allMatching.size());
        List<MallOrder> page = start < allMatching.size() ? allMatching.subList(start, end) : List.of();

        List<Map<String, Object>> list = new ArrayList<>();
        for (MallOrder o : page) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", o.getUuid());
            item.put("orderId", o.getUuid());
            item.put("orderNo", o.getOrderNo());
            item.put("buyerName", o.getReceiverName());
            item.put("amount", o.getPayAmount());
            item.put("totalAmount", o.getTotalAmount());
            item.put("payAmount", o.getPayAmount());
            item.put("orderStatus", o.getOrderStatus());
            item.put("reason", o.getRemark());
            item.put("createTime", o.getCreateTime());
            list.add(item);
        }
        return Map.of("total", total, "list", list);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void refundProcess(Long merchantId, String orderId, Boolean approved) {
        MallOrder order = orderMapper.selectById(orderId);
        if (order == null) throw new BizException("订单不存在");
        if (order.getOrderStatus() != 5) throw new BizException("该订单无退款申请");

        List<MallOrdersGoods> goods = ordersGoodsMapper.selectList(
            new QueryWrapper<MallOrdersGoods>().eq("order_id", order.getUuid()));
        List<String> goodIds = goods.stream().map(MallOrdersGoods::getGoodsId).toList();
        List<Product> orderProducts = goodIds.isEmpty() ? List.of() :
            productMapper.selectBatchIds(goodIds.stream().map(Long::valueOf).toList());
        boolean ownsProduct = orderProducts.stream()
            .anyMatch(p -> merchantId.equals(p.getMerchantId()));
        if (!ownsProduct) throw new BizException("无权操作此订单");

        Long userId = Long.valueOf(order.getPartyId());
        if (approved) {
            order.setOrderStatus(6);
            orderMapper.updateById(order);
            UserBalance balance = userBalanceMapper.selectOne(
                new QueryWrapper<UserBalance>().eq("user_id", userId));
            if (balance != null) {
                userBalanceMapper.addBalance(userId, order.getPayAmount());
                balanceLogMapper.insert(BalanceLog.builder()
                    .userId(userId).amount(order.getPayAmount())
                    .type("REFUND").remark("退款：" + order.getOrderNo())
                    .relatedId(null).build());
            }
        } else {
            order.setOrderStatus(7);
            orderMapper.updateById(order);
        }
    }

    // ==================== Wallet ====================

    @Override
    public Map<String, Object> walletInfo(Long merchantId) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");

        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", merchant.getUserId()));
        Map<String, Object> info = new HashMap<>();
        info.put("balance", balance != null ? balance.getBalance() : BigDecimal.ZERO);
        info.put("frozen", balance != null ? balance.getFrozen() : BigDecimal.ZERO);
        info.put("available", balance != null ? UserBalanceUtil.getAvailable(balance) : BigDecimal.ZERO);
        return info;
    }

    @Override
    public Map<String, Object> rechargeList(Long merchantId, Integer pageNum, Integer pageSize) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");
        IPage<RechargeOrder> page = rechargeOrderMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<RechargeOrder>().eq("user_id", merchant.getUserId()).orderByDesc("create_time"));
        return Map.of("total", page.getTotal(), "list", page.getRecords());
    }

    @Override
    public Map<String, Object> withdrawList(Long merchantId, Integer pageNum, Integer pageSize) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");
        IPage<WithdrawOrder> page = withdrawOrderMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<WithdrawOrder>().eq("user_id", merchant.getUserId()).orderByDesc("create_time"));
        return Map.of("total", page.getTotal(), "list", page.getRecords());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void rechargeApply(Long merchantId, Map<String, Object> data) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");

        BigDecimal amount = new BigDecimal(data.get("amount").toString());
        if (amount.compareTo(BigDecimal.ZERO) <= 0) throw new BizException("充值金额必须大于0");

        String txHash = data.get("txHash") != null ? data.get("txHash").toString() : null;
        if (txHash != null && !txHash.isBlank()) {
            Long count = rechargeOrderMapper.selectCount(
                new QueryWrapper<RechargeOrder>().eq("tx_hash", txHash));
            if (count > 0) throw new BizException("该链上交易已被提交过充值申请");
        }

        RechargeOrder order = RechargeOrder.builder()
            .orderNo(OrderNoUtil.generateRechargeNo())
            .userId(merchant.getUserId())
            .amount(amount)
            .usdtAddress(data.get("usdtAddress") != null ? data.get("usdtAddress").toString() : null)
            .txHash(txHash)
            .screenshot(data.get("screenshot") != null ? data.get("screenshot").toString() : null)
            .status(0)
            .build();
        rechargeOrderMapper.insert(order);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void withdrawApply(Long merchantId, Map<String, Object> data) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");

        BigDecimal amount = new BigDecimal(data.get("amount").toString());
        if (amount.compareTo(BigDecimal.ZERO) <= 0) throw new BizException("提现金额必须大于0");

        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", merchant.getUserId()));
        if (balance == null || UserBalanceUtil.getAvailable(balance).compareTo(amount) < 0)
            throw new BizException("可用余额不足");

        int rows = userBalanceMapper.deductBalance(merchant.getUserId(), amount, balance.getVersion());
        if (rows == 0) throw new BizException("余额扣减失败，请重试");

        WithdrawOrder order = WithdrawOrder.builder()
            .orderNo(OrderNoUtil.generateWithdrawNo())
            .userId(merchant.getUserId())
            .amount(amount)
            .usdtAddress(data.get("usdtAddress").toString())
            .status(0)
            .build();
        withdrawOrderMapper.insert(order);

        balanceLogMapper.insert(BalanceLog.builder()
            .userId(merchant.getUserId()).amount(amount.negate())
            .type("WITHDRAW").remark("提现申请：" + order.getOrderNo()).build());
    }

    // ==================== Balance Log ====================

    @Override
    public Map<String, Object> balanceLogList(Long merchantId, Integer pageNum, Integer pageSize) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");
        IPage<BalanceLog> page = balanceLogMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<BalanceLog>().eq("user_id", merchant.getUserId()).orderByDesc("create_time"));
        return Map.of("total", page.getTotal(), "list", page.getRecords());
    }

    // ==================== Financial Report ====================

    @Override
    public Map<String, Object> financeReport(Long merchantId, String startDate, String endDate) {
        List<Product> products = productMapper.selectList(
            new QueryWrapper<Product>().eq("merchant_id", merchantId));
        if (products.isEmpty()) {
            return Map.of("totalRevenue", BigDecimal.ZERO, "totalOrders", 0L,
                "totalRefunds", BigDecimal.ZERO, "dailyStats", List.of());
        }
        List<String> productIds = products.stream().map(p -> p.getId().toString()).toList();

        List<MallOrdersGoods> allGoods = ordersGoodsMapper.selectList(
            new QueryWrapper<MallOrdersGoods>().in("goods_id", productIds));
        Set<String> orderIds = allGoods.stream()
            .map(MallOrdersGoods::getOrderId).collect(Collectors.toSet());
        if (orderIds.isEmpty()) {
            return Map.of("totalRevenue", BigDecimal.ZERO, "totalOrders", 0L,
                "totalRefunds", BigDecimal.ZERO, "dailyStats", List.of());
        }

        QueryWrapper<MallOrder> qw = new QueryWrapper<MallOrder>()
            .in("uuid", orderIds)
            .ge(startDate != null && !startDate.isBlank(), "create_time", startDate + " 00:00:00")
            .le(endDate != null && !endDate.isBlank(), "create_time", endDate + " 23:59:59")
            .orderByAsc("create_time");
        List<MallOrder> orders = orderMapper.selectList(qw);

        BigDecimal totalRevenue = BigDecimal.ZERO;
        BigDecimal totalRefunds = BigDecimal.ZERO;
        Map<String, BigDecimal[]> dailyMap = new LinkedHashMap<>();

        for (MallOrder o : orders) {
            String day = o.getCreateTime() != null ?
                o.getCreateTime().toLocalDate().toString() : "";
            dailyMap.putIfAbsent(day, new BigDecimal[]{BigDecimal.ZERO, BigDecimal.ZERO});
            if (o.getOrderStatus() == 4 || o.getOrderStatus() == 6) {
                totalRefunds = totalRefunds.add(o.getPayAmount() != null ? o.getPayAmount() : BigDecimal.ZERO);
                dailyMap.get(day)[1] = dailyMap.get(day)[1].add(o.getPayAmount() != null ? o.getPayAmount() : BigDecimal.ZERO);
            } else if (o.getOrderStatus() != 7) {
                totalRevenue = totalRevenue.add(o.getPayAmount() != null ? o.getPayAmount() : BigDecimal.ZERO);
                dailyMap.get(day)[0] = dailyMap.get(day)[0].add(o.getPayAmount() != null ? o.getPayAmount() : BigDecimal.ZERO);
            }
        }

        List<Map<String, Object>> dailyStats = new ArrayList<>();
        for (Map.Entry<String, BigDecimal[]> e : dailyMap.entrySet()) {
            dailyStats.add(Map.of("date", e.getKey(),
                "revenue", e.getValue()[0], "refunds", e.getValue()[1]));
        }

        Map<String, Object> result = new HashMap<>();
        result.put("totalRevenue", totalRevenue);
        result.put("totalOrders", (long) orders.size());
        result.put("totalRefunds", totalRefunds);
        result.put("dailyStats", dailyStats);
        return result;
    }

    // ==================== Customer Service ====================

    @Override
    public Map<String, Object> chatList(Long merchantId, Integer pageNum, Integer pageSize) {
        IPage<ChatMessage> page = chatMessageMapper.selectPage(new Page<>(pageNum, pageSize),
            new QueryWrapper<ChatMessage>().eq("to_user_id", merchantId)
                .orderByDesc("create_time"));
        return Map.of("total", page.getTotal(), "list", page.getRecords());
    }

    @Override
    public Map<String, Object> chatConversation(Long merchantId, Long fromUserId) {
        List<ChatMessage> messages = chatMessageMapper.selectList(
            new QueryWrapper<ChatMessage>()
                .and(w -> w.eq("from_user_id", fromUserId).eq("to_user_id", merchantId)
                    .or().eq("from_user_id", merchantId).eq("to_user_id", fromUserId))
                .orderByAsc("create_time"));
        return Map.of("list", messages);
    }

    @Override
    public void chatReply(Long merchantId, Long toUserId, String content) {
        ChatMessage msg = ChatMessage.builder()
            .conversationId(merchantId + "_" + toUserId)
            .fromUserId(merchantId)
            .toUserId(toUserId)
            .content(content)
            .msgType("TEXT")
            .isRead(0)
            .build();
        chatMessageMapper.insert(msg);
    }

    // ==================== Settle (Merchant Apply) ====================

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void settle(Map<String, Object> data) {
        String phone = data.get("contactPhone") != null ? data.get("contactPhone").toString() : null;
        String username = data.get("username") != null ? data.get("username").toString() : phone;
        String password = data.get("password") != null ? data.get("password").toString() : null;
        if (phone == null || phone.isBlank()) throw new BizException("联系电话不能为空");
        if (password == null || password.length() < 6) throw new BizException("密码至少6位");
        if (data.get("shopName") == null || data.get("shopName").toString().isBlank())
            throw new BizException("店铺名称不能为空");

        // check duplicate application by phone
        Long cnt = merchantApplyMapper.selectCount(
            new QueryWrapper<MerchantApply>().eq("shop_phone", phone).eq("status", 0));
        if (cnt > 0) throw new BizException("您已有申请正在审核中，请耐心等待");

        // check if phone already registered as user
        User existUser = userMapper.selectOne(new QueryWrapper<User>().eq("phone", phone));
        Long userId;
        if (existUser != null) {
            userId = existUser.getId();
        } else {
            // also check username duplicate
            User existName = userMapper.selectOne(new QueryWrapper<User>().eq("phone", username));
            if (existName != null) throw new BizException("用户名已被使用，请更换");

            User newUser = User.builder()
                .phone(username)  // use username as phone field for login
                .nickname(data.get("contactName") != null ? data.get("contactName").toString() : username)
                .password(passwordEncoder.encode(password))
                .email(data.get("contactEmail") != null ? data.get("contactEmail").toString() : null)
                .status(0)
                .levelId(0)
                .build();
            userMapper.insert(newUser);
            userId = newUser.getId();
        }

        String remark = data.get("shopDesc") != null ? data.get("shopDesc").toString() : "";
        if (data.get("licenseUrl") != null) remark += " | license:" + data.get("licenseUrl");
        if (data.get("idFrontUrl") != null) remark += " | idFront:" + data.get("idFrontUrl");
        if (data.get("idBackUrl") != null) remark += " | idBack:" + data.get("idBackUrl");

        MerchantApply apply = MerchantApply.builder()
            .userId(userId)
            .shopName(data.get("shopName").toString())
            .shopPhone(phone)
            .contact(data.get("contactName") != null ? data.get("contactName").toString() : "")
            .remark(remark)
            .status(0)
            .createTime(LocalDateTime.now())
            .build();
        merchantApplyMapper.insert(apply);
    }

    @Override
    public Map<String, Object> settleStatus(String phone) {
        if (phone == null || phone.isBlank()) throw new BizException("手机号不能为空");
        MerchantApply apply = merchantApplyMapper.selectOne(
            new QueryWrapper<MerchantApply>().eq("shop_phone", phone).orderByDesc("create_time").last("LIMIT 1"));
        if (apply == null) {
            return Map.of("found", false, "status", -1, "statusText", "未找到申请记录");
        }
        String statusText = switch (apply.getStatus()) {
            case 0 -> "审核中";
            case 1 -> "已通过";
            case 2 -> "已拒绝";
            default -> "未知";
        };
        Map<String, Object> result = new HashMap<>();
        result.put("found", true);
        result.put("status", apply.getStatus());
        result.put("statusText", statusText);
        result.put("shopName", apply.getShopName());
        result.put("rejectReason", apply.getRejectReason() != null ? apply.getRejectReason() : "");
        result.put("auditTime", apply.getAuditTime() != null ? apply.getAuditTime().toString() : null);
        result.put("createTime", apply.getCreateTime() != null ? apply.getCreateTime().toString() : null);
        return result;
    }

    // ==================== Account ====================

    @Override
    @Transactional
    public void deleteAccount(Long merchantId, String password, String reason) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");

        User user = userMapper.selectById(merchant.getUserId());
        if (user == null || !passwordEncoder.matches(password, user.getPassword()))
            throw new BizException("密码错误");

        Long uid = merchant.getUserId();
        Long unfinishedWithdraws = withdrawOrderMapper.selectCount(
            new QueryWrapper<WithdrawOrder>().eq("user_id", uid).eq("status", 0));
        if (unfinishedWithdraws > 0) throw new BizException("有未完成的提现订单，请先处理");

        Long unfinishedRecharges = rechargeOrderMapper.selectCount(
            new QueryWrapper<RechargeOrder>().eq("user_id", uid).eq("status", 0));
        if (unfinishedRecharges > 0) throw new BizException("有未完成的充值订单，请先处理");

        merchant.setStatus(0);
        merchantMapper.updateById(merchant);

        user.setStatus(-1);
        userMapper.updateById(user);
    }

    // ==================== Library ====================

    @Override
    public Map<String, Object> libraryList(String keyword, Integer pageNum, Integer pageSize) {
        int p = pageNum == null || pageNum < 1 ? 1 : pageNum;
        int ps = pageSize == null || pageSize < 1 ? 20 : pageSize;
        QueryWrapper<SystemGoods> qw = new QueryWrapper<>();
        qw.eq("status", 1);
        if (keyword != null && !keyword.isEmpty()) qw.like("goods_name", keyword);
        qw.orderByDesc("create_time");
        Page<SystemGoods> pg = new Page<>(p, ps);
        Page<SystemGoods> result = systemGoodsMapper.selectPage(pg, qw);
        List<Map<String, Object>> records = new ArrayList<>();
        for (SystemGoods g : result.getRecords()) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("id", g.getUuid());
            item.put("goodsName", g.getGoodsName());
            item.put("image", g.getMainImage());
            item.put("price", g.getSystemPrice());
            item.put("categoryId", g.getCategoryId());
            item.put("brandName", g.getBrandName());
            records.add(item);
        }
        Map<String, Object> r = new HashMap<>();
        r.put("records", records);
        r.put("total", result.getTotal());
        return r;
    }

    @Override
    @Transactional
    public void libraryPurchase(Long merchantId, String systemGoodsId) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");

        SystemGoods sysGoods = systemGoodsMapper.selectById(systemGoodsId);
        if (sysGoods == null) throw new BizException("商品不存在");
        if (sysGoods.getStatus() == null || sysGoods.getStatus() != 1)
            throw new BizException("商品已下架");

        BigDecimal price = new BigDecimal(sysGoods.getSystemPrice());
        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", merchant.getUserId()));
        if (balance == null) throw new BizException("余额账户不存在");

        BigDecimal available = UserBalanceUtil.getAvailable(balance);
        if (available.compareTo(price) < 0) throw new BizException("可用余额不足");

        int rows = userBalanceMapper.update(null,
            new UpdateWrapper<UserBalance>()
                .eq("user_id", merchant.getUserId())
                .eq("version", balance.getVersion())
                .setSql("balance = balance - " + price)
                .setSql("version = version + 1")
                .set("update_time", LocalDateTime.now()));
        if (rows == 0) throw new BizException("扣款失败，请重试");

        BalanceLog log = BalanceLog.builder()
            .userId(merchant.getUserId())
            .amount(price.negate())
            .type("LIBRARY_BUY")
            .remark("购买商品库商品: " + systemGoodsId)
            .createTime(LocalDateTime.now())
            .build();
        balanceLogMapper.insert(log);

        Product product = Product.builder()
            .merchantId(merchantId)
            .name(sysGoods.getGoodsName())
            .description(sysGoods.getGoodsDesc())
            .price(price)
            .mainImage(sysGoods.getMainImage())
            .status(0)
            .createTime(LocalDateTime.now())
            .updateTime(LocalDateTime.now())
            .build();
        productMapper.insert(product);
    }

    // ==================== Car / Promote ====================

    @Override
    @Transactional
    public void carBuy(Long merchantId, Integer days) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");

        BigDecimal price;
        if (days == 7) price = new BigDecimal("50");
        else if (days == 15) price = new BigDecimal("90");
        else if (days == 30) price = new BigDecimal("150");
        else throw new BizException("不支持的天数");

        UserBalance balance = userBalanceMapper.selectOne(
            new QueryWrapper<UserBalance>().eq("user_id", merchant.getUserId()));
        if (balance == null) throw new BizException("余额账户不存在");

        BigDecimal available = UserBalanceUtil.getAvailable(balance);
        if (available.compareTo(price) < 0) throw new BizException("可用余额不足");

        int rows = userBalanceMapper.update(null,
            new UpdateWrapper<UserBalance>()
                .eq("user_id", merchant.getUserId())
                .eq("version", balance.getVersion())
                .setSql("balance = balance - " + price)
                .setSql("version = version + 1")
                .set("update_time", LocalDateTime.now()));
        if (rows == 0) throw new BizException("扣款失败，请重试");

        BalanceLog log = BalanceLog.builder()
            .userId(merchant.getUserId())
            .amount(price.negate())
            .type("CAR_BUY")
            .remark("购买直通车: " + days + "天")
            .createTime(LocalDateTime.now())
            .build();
        balanceLogMapper.insert(log);

        long now = System.currentTimeMillis();
        MallComboRecord cr = new MallComboRecord();
        cr.setUuid(UUID.randomUUID().toString().replace("-", ""));
        cr.setPartyId(merchant.getUserId().toString());
        cr.setComboId("CAR_" + days);
        cr.setAmount(price);
        cr.setDay(days);
        cr.setPromoteNum(100);
        cr.setCreateTime(LocalDateTime.now());
        cr.setBeginTime(now);
        cr.setStopTime(now + days * 86400000L);
        comboRecordMapper.insert(cr);
    }

    @Override
    public List<Map<String, Object>> carHistory(Long merchantId) {
        Merchant merchant = merchantMapper.selectById(merchantId);
        if (merchant == null) throw new BizException("商家不存在");

        long now = System.currentTimeMillis();
        List<MallComboRecord> records = comboRecordMapper.selectList(
            new QueryWrapper<MallComboRecord>()
                .eq("party_id", merchant.getUserId().toString())
                .like("combo_id", "CAR_")
                .orderByDesc("create_time"));

        List<Map<String, Object>> list = new ArrayList<>();
        for (MallComboRecord cr : records) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("days", cr.getDay());
            map.put("amount", cr.getAmount());
            map.put("startTime", cr.getBeginTime() != null ?
                new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm").format(new java.util.Date(cr.getBeginTime())) : "");
            map.put("endTime", cr.getStopTime() != null ?
                new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm").format(new java.util.Date(cr.getStopTime())) : "");
            map.put("status", cr.getStopTime() != null && cr.getStopTime() > now ? 1 : 0);
            list.add(map);
        }
        return list;
    }

    // ==================== SKU Management ====================

    @Override
    public List<ProductSku> skuList(Long merchantId, String productId) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        if (!merchantId.equals(product.getMerchantId())) throw new BizException("无权查看此商品");
        return skuMapper.selectList(
            new QueryWrapper<ProductSku>().eq("good_id", productId).eq("deleted", 0));
    }

    @Override
    public void skuAdd(Long merchantId, String productId, Map<String, Object> data) {
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        if (!merchantId.equals(product.getMerchantId())) throw new BizException("无权操作此商品");

        ProductSku sku = ProductSku.builder()
            .id(java.util.UUID.randomUUID().toString().replace("-", "").substring(0, 32))
            .goodId(productId)
            .price(data.get("price") != null ? new BigDecimal(data.get("price").toString()) : BigDecimal.ZERO)
            .promotionPrice(data.get("promotionPrice") != null ? new BigDecimal(data.get("promotionPrice").toString()) : null)
            .sale(data.get("sale") != null ? Integer.parseInt(data.get("sale").toString()) : 0)
            .spData(data.get("spData") != null ? data.get("spData").toString() : null)
            .pic(data.get("pic") != null ? data.get("pic").toString() : null)
            .coverImg(data.get("coverImg") != null ? data.get("coverImg").toString() : null)
            .iconImg(data.get("iconImg") != null ? data.get("iconImg").toString() : null)
            .deleted(0)
            .build();
        skuMapper.insert(sku);
    }

    @Override
    public void skuUpdate(Long merchantId, String skuId, Map<String, Object> data) {
        ProductSku sku = skuMapper.selectById(skuId);
        if (sku == null) throw new BizException("SKU不存在");
        String productId = sku.getGoodId();
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        if (!merchantId.equals(product.getMerchantId())) throw new BizException("无权操作此商品");

        if (data.containsKey("price")) sku.setPrice(new BigDecimal(data.get("price").toString()));
        if (data.containsKey("promotionPrice")) sku.setPromotionPrice(data.get("promotionPrice") != null ? new BigDecimal(data.get("promotionPrice").toString()) : null);
        if (data.containsKey("sale")) sku.setSale(Integer.parseInt(data.get("sale").toString()));
        if (data.containsKey("spData")) sku.setSpData(data.get("spData") != null ? data.get("spData").toString() : null);
        if (data.containsKey("pic")) sku.setPic(data.get("pic") != null ? data.get("pic").toString() : null);
        if (data.containsKey("coverImg")) sku.setCoverImg(data.get("coverImg") != null ? data.get("coverImg").toString() : null);
        if (data.containsKey("iconImg")) sku.setIconImg(data.get("iconImg") != null ? data.get("iconImg").toString() : null);
        skuMapper.updateById(sku);
    }

    @Override
    public void skuDelete(Long merchantId, String skuId) {
        ProductSku sku = skuMapper.selectById(skuId);
        if (sku == null) throw new BizException("SKU不存在");
        String productId = sku.getGoodId();
        Product product = productMapper.selectById(productId);
        if (product == null) throw new BizException("商品不存在");
        if (!merchantId.equals(product.getMerchantId())) throw new BizException("无权操作此商品");
        sku.setDeleted(1);
        skuMapper.updateById(sku);
    }
}
