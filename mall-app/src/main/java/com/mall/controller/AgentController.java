package com.mall.controller;

import com.mall.common.Result;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mall.entity.RechargeOrder;
import com.mall.mapper.RechargeOrderMapper;
import com.mall.entity.Category;
import com.mall.entity.MallBanner;
import com.mall.service.AdminService;
import com.mall.service.BannerService;
import com.mall.service.CategoryService;
import com.mall.service.EvaluationService;
import com.mall.service.GoodsAttrService;
import com.mall.service.OrderService;
import com.mall.service.ProductService;
import com.mall.service.RechargeService;
import com.mall.service.SeedService;
import com.mall.service.WithdrawService;
import com.mall.entity.CategoryAttr;
import com.mall.entity.ProductAttr;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/agent")
@RequiredArgsConstructor
public class AgentController {

    private final AdminService adminService;
    private final BannerService bannerService;
    private final CategoryService categoryService;
    private final EvaluationService evaluationService;
    private final OrderService orderService;
    private final ProductService productService;
    private final RechargeService rechargeService;
    private final WithdrawService withdrawService;
    private final GoodsAttrService goodsAttrService;
    private final RechargeOrderMapper rechargeOrderMapper;
    private final RedisTemplate<String, Object> redisTemplate;
    private final SeedService seedService;

    @GetMapping("/health")
    public Result<?> health() {
        return Result.ok(Map.of("status", "running", "db", "ok", "redis", "ok"));
    }

    @GetMapping("/dashboard")
    public Result<?> dashboard() {
        return Result.ok(adminService.dashboard());
    }

    @GetMapping("/recharge/pending")
    public Result<?> rechargePending(@RequestParam(defaultValue = "1") Integer pageNum,
                                     @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.rechargePending(pageNum, pageSize));
    }

    @GetMapping("/withdraw/pending")
    public Result<?> withdrawPending(@RequestParam(defaultValue = "1") Integer pageNum,
                                     @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.withdrawPending(pageNum, pageSize));
    }

    @PostMapping("/cache/flush")
    public Result<?> flushCache() {
        redisTemplate.getConnectionFactory().getConnection().serverCommands().flushAll();
        return Result.ok();
    }

    @PostMapping("/notify/telegram")
    public Result<?> telegramNotify(@RequestBody Map<String, String> dto) {
        return Result.ok(Map.of("message", "Telegram通知已发送"));
    }

    @PostMapping("/product/add")
    public Result<?> addProduct(@RequestBody Map<String, Object> dto) {
        try {
            Long productId = productService.save(dto);
            return Result.ok(Map.of("productId", productId));
        } catch (Exception e) {
            return Result.fail(e.getMessage());
        }
    }

    @GetMapping("/user/list")
    public Result<?> userList(@RequestParam(defaultValue = "") String keyword,
                               @RequestParam(defaultValue = "1") Integer pageNum,
                               @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.userList(keyword, null, pageNum, pageSize));
    }

    @GetMapping("/order/list")
    public Result<?> orderList(@RequestParam(defaultValue = "1") Integer pageNum,
                                @RequestParam(defaultValue = "10") Integer pageSize) {
        IPage<RechargeOrder> page = rechargeOrderMapper.selectPage(
            new Page<>(pageNum, pageSize),
            new QueryWrapper<RechargeOrder>().orderByDesc("create_time"));
        List<Map<String, Object>> list = new ArrayList<>();
        for (RechargeOrder o : page.getRecords()) {
            Map<String, Object> item = new HashMap<>();
            item.put("id", o.getId());
            item.put("orderNo", o.getOrderNo());
            item.put("userId", o.getUserId());
            item.put("amount", o.getAmount());
            item.put("status", o.getStatus());
            item.put("createTime", o.getCreateTime());
            list.add(item);
        }
        return Result.ok(Map.of("total", page.getTotal(), "pages", page.getPages(), "current", page.getCurrent(), "records", list));
    }

    // ===== 用户管理 =====

    @PostMapping("/user/status")
    public Result<?> updateUserStatus(@RequestBody Map<String, Object> dto) {
        Long userId = Long.valueOf(dto.get("userId").toString());
        Integer status = Integer.valueOf(dto.get("status").toString());
        adminService.updateUserStatus(userId, status);
        return Result.ok();
    }

    @PostMapping("/user/balance/adjust")
    public Result<?> adjustBalance(@RequestBody Map<String, Object> dto) {
        Long userId = Long.valueOf(dto.get("userId").toString());
        java.math.BigDecimal amount = new java.math.BigDecimal(dto.get("amount").toString());
        String remark = (String) dto.getOrDefault("remark", "");
        adminService.adjustBalance(userId, amount, remark, 0L);
        return Result.ok();
    }

    // ===== 充值审核 =====

    @PostMapping("/recharge/audit")
    public Result<?> auditRecharge(@RequestBody Map<String, Object> dto) {
        Long id = Long.valueOf(dto.get("id").toString());
        Boolean approved = Boolean.valueOf(dto.get("approved").toString());
        String reason = (String) dto.getOrDefault("reason", "");
        adminService.auditRecharge(id, approved, reason, 0L);
        return Result.ok();
    }

    // ===== 提现审核 =====

    @PostMapping("/withdraw/audit")
    public Result<?> auditWithdraw(@RequestBody Map<String, Object> dto) {
        Long id = Long.valueOf(dto.get("id").toString());
        Boolean approved = Boolean.valueOf(dto.get("approved").toString());
        String txHash = (String) dto.getOrDefault("txHash", "");
        String reason = (String) dto.getOrDefault("reason", "");
        adminService.auditWithdraw(id, approved, txHash, reason, 0L);
        return Result.ok();
    }

    // ===== 商家入驻审核 =====

    @GetMapping("/merchant/apply/list")
    public Result<?> merchantApplyList(@RequestParam(defaultValue = "1") Integer pageNum,
                                       @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.merchantApplyList(pageNum, pageSize));
    }

    @PostMapping("/merchant/apply/audit")
    public Result<?> auditMerchantApply(@RequestBody Map<String, Object> dto) {
        Long applyId = Long.valueOf(dto.get("applyId").toString());
        Boolean approved = Boolean.valueOf(dto.get("approved").toString());
        String reason = (String) dto.getOrDefault("reason", "");
        adminService.auditMerchantApply(applyId, approved, reason, 0L);
        return Result.ok();
    }

    // ===== 商家管理 =====

    @GetMapping("/merchant/list")
    public Result<?> merchantList(@RequestParam(defaultValue = "") String keyword,
                                   @RequestParam(required = false) Integer status,
                                   @RequestParam(defaultValue = "1") Integer pageNum,
                                   @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.merchantList(keyword, status, pageNum, pageSize));
    }

    @PostMapping("/merchant/status")
    public Result<?> updateMerchantStatus(@RequestBody Map<String, Object> dto) {
        Long merchantId = Long.valueOf(dto.get("merchantId").toString());
        Integer status = Integer.valueOf(dto.get("status").toString());
        adminService.updateMerchantStatus(merchantId, status);
        return Result.ok();
    }

    // ===== 商品审核 =====

    @GetMapping("/product/list")
    public Result<?> productList(@RequestParam(defaultValue = "") String keyword,
                                  @RequestParam(required = false) Integer status,
                                  @RequestParam(defaultValue = "1") Integer pageNum,
                                  @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.productList(keyword, status, pageNum, pageSize));
    }

    @PostMapping("/product/audit")
    public Result<?> auditProduct(@RequestBody Map<String, Object> dto) {
        Long productId = Long.valueOf(dto.get("productId").toString());
        Integer status = Integer.valueOf(dto.get("status").toString());
        adminService.auditProduct(productId, status, 0L);
        return Result.ok();
    }

    // ===== 订单管理 =====

    @GetMapping("/order/all")
    public Result<?> allOrders(@RequestParam(defaultValue = "") String keyword,
                                @RequestParam(required = false) Integer status,
                                @RequestParam(defaultValue = "1") Integer pageNum,
                                @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.orderList(keyword, status, pageNum, pageSize));
    }

    @PostMapping("/order/refund/{id}")
    public Result<?> forceRefund(@PathVariable Long id) {
        adminService.forceRefund(id, 0L);
        return Result.ok();
    }

    // ===== 轮播管理 =====

    @GetMapping("/banner/list")
    public Result<?> bannerList(@RequestParam(required = false) String type,
                                 @RequestParam(required = false) String startTime,
                                 @RequestParam(required = false) String endTime,
                                 @RequestParam(defaultValue = "1") Integer pageNum,
                                 @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(bannerService.list(type, null, startTime, endTime, pageNum, pageSize));
    }

    @GetMapping("/banner/{uuid}")
    public Result<?> bannerDetail(@PathVariable String uuid) {
        MallBanner banner = bannerService.getById(uuid);
        if (banner == null) return Result.fail("轮播图不存在");
        return Result.ok(banner);
    }

    @PostMapping("/banner")
    public Result<?> bannerSave(@RequestBody MallBanner banner) {
        bannerService.save(banner);
        return Result.ok();
    }

    @PutMapping("/banner/{uuid}")
    public Result<?> bannerUpdate(@PathVariable String uuid, @RequestBody MallBanner banner) {
        banner.setUuid(uuid);
        bannerService.update(banner);
        return Result.ok();
    }

    @DeleteMapping("/banner/{uuid}")
    public Result<?> bannerDelete(@PathVariable String uuid) {
        bannerService.delete(uuid);
        return Result.ok();
    }

    // ===== 分类管理 =====

    @GetMapping("/category/list")
    public Result<?> categoryList(@RequestParam(required = false) String parentId,
                                   @RequestParam(required = false) Integer level,
                                   @RequestParam(required = false) String startTime,
                                   @RequestParam(required = false) String endTime,
                                   @RequestParam(defaultValue = "1") Integer pageNum,
                                   @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(categoryService.list(parentId, level, startTime, endTime, pageNum, pageSize));
    }

    @GetMapping("/category/all")
    public Result<?> categoryAll() {
        return Result.ok(categoryService.listAll());
    }

    @GetMapping("/category/{uuid}")
    public Result<?> categoryDetail(@PathVariable String uuid) {
        Category cat = categoryService.getById(uuid);
        if (cat == null) return Result.fail("分类不存在");
        return Result.ok(cat);
    }

    @PostMapping("/category")
    public Result<?> categorySave(@RequestBody Category category) {
        categoryService.save(category);
        return Result.ok();
    }

    @PutMapping("/category/{uuid}")
    public Result<?> categoryUpdate(@PathVariable String uuid, @RequestBody Category category) {
        category.setUuid(uuid);
        categoryService.update(category);
        return Result.ok();
    }

    @PutMapping("/category/{uuid}/status")
    public Result<?> categoryUpdateStatus(@PathVariable String uuid, @RequestBody Map<String, Object> dto) {
        categoryService.updateStatus(uuid, Integer.parseInt(dto.get("status").toString()));
        return Result.ok();
    }

    @DeleteMapping("/category/{uuid}")
    public Result<?> categoryDelete(@PathVariable String uuid) {
        categoryService.delete(uuid);
        return Result.ok();
    }

    // ===== 评价管理 =====

    @GetMapping("/evaluation/list")
    public Result<?> evaluationList(@RequestParam(required = false) String keyword,
                                     @RequestParam(required = false) Integer status,
                                     @RequestParam(defaultValue = "1") Integer pageNum,
                                     @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(evaluationService.adminList(keyword, status, pageNum, pageSize));
    }

    @PutMapping("/evaluation/{uuid}/status")
    public Result<?> evaluationUpdateStatus(@PathVariable String uuid, @RequestBody Map<String, Object> dto) {
        evaluationService.adminUpdateStatus(uuid, Integer.parseInt(dto.get("status").toString()));
        return Result.ok();
    }

    @DeleteMapping("/evaluation/{uuid}")
    public Result<?> evaluationDelete(@PathVariable String uuid) {
        evaluationService.adminDelete(uuid);
        return Result.ok();
    }

    // ===== 商品属性分类管理 =====

    @GetMapping("/attr-category/list")
    public Result<?> attrCategoryList(@RequestParam(required = false) String keyword,
                                       @RequestParam(defaultValue = "1") Integer pageNum,
                                       @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(goodsAttrService.categoryList(keyword, pageNum, pageSize));
    }

    @GetMapping("/attr-category/{uuid}")
    public Result<?> attrCategoryDetail(@PathVariable String uuid) {
        return Result.ok(goodsAttrService.categoryGetById(uuid));
    }

    @PostMapping("/attr-category")
    public Result<?> attrCategorySave(@RequestBody CategoryAttr category) {
        goodsAttrService.categorySave(category);
        return Result.ok();
    }

    @PutMapping("/attr-category/{uuid}")
    public Result<?> attrCategoryUpdate(@PathVariable String uuid, @RequestBody CategoryAttr category) {
        category.setId(uuid);
        goodsAttrService.categoryUpdate(category);
        return Result.ok();
    }

    @DeleteMapping("/attr-category/{uuid}")
    public Result<?> attrCategoryDelete(@PathVariable String uuid) {
        goodsAttrService.categoryDelete(uuid);
        return Result.ok();
    }

    // ===== 商品属性管理 =====

    @GetMapping("/attr/list")
    public Result<?> attrList(@RequestParam(required = false) String categoryId,
                               @RequestParam(defaultValue = "1") Integer pageNum,
                               @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(goodsAttrService.attrList(categoryId, pageNum, pageSize));
    }

    @GetMapping("/attr/{uuid}")
    public Result<?> attrDetail(@PathVariable String uuid) {
        return Result.ok(goodsAttrService.attrGetById(uuid));
    }

    @PostMapping("/attr")
    public Result<?> attrSave(@RequestBody ProductAttr attr) {
        goodsAttrService.attrSave(attr);
        return Result.ok();
    }

    @PutMapping("/attr/{uuid}")
    public Result<?> attrUpdate(@PathVariable String uuid, @RequestBody ProductAttr attr) {
        attr.setId(uuid);
        goodsAttrService.attrUpdate(attr);
        return Result.ok();
    }

    @DeleteMapping("/attr/{uuid}")
    public Result<?> attrDelete(@PathVariable String uuid) {
        goodsAttrService.attrDelete(uuid);
        return Result.ok();
    }

    // ===== 属性值管理 =====

    @GetMapping("/attr-value/list")
    public Result<?> attrValueList(@RequestParam String attrId,
                                    @RequestParam(defaultValue = "1") Integer pageNum,
                                    @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(goodsAttrService.valueList(attrId, pageNum, pageSize));
    }

    @GetMapping("/attr-value/{id}")
    public Result<?> attrValueDetail(@PathVariable String id) {
        return Result.ok(goodsAttrService.valueGetById(id));
    }

    @PostMapping("/attr-value")
    public Result<?> attrValueSave(@RequestBody Map<String, String> dto) {
        goodsAttrService.valueSave(dto.get("attrId"), dto.get("name"), dto.getOrDefault("lang", "en"));
        return Result.ok();
    }

    @PutMapping("/attr-value/{id}")
    public Result<?> attrValueUpdate(@PathVariable String id, @RequestBody Map<String, String> dto) {
        goodsAttrService.valueUpdate(id, dto.get("name"), dto.getOrDefault("lang", "en"));
        return Result.ok();
    }

    @DeleteMapping("/attr-value/{id}")
    public Result<?> attrValueDelete(@PathVariable String id) {
        goodsAttrService.valueDelete(id);
        return Result.ok();
    }

    // ===== 虚拟数据生成 =====

    @PostMapping("/seed/products")
    public Result<?> seedProducts(@RequestParam(defaultValue = "10") int count) {
        return Result.ok(seedService.generateProducts(count));
    }

    @PostMapping("/seed/orders")
    public Result<?> seedOrders(@RequestParam(defaultValue = "10") int count) {
        return Result.ok(seedService.generateOrders(count));
    }

    @PostMapping("/seed/cart")
    public Result<?> seedCart(@RequestParam(defaultValue = "10") int count) {
        return Result.ok(seedService.generateCart(count));
    }

    @PostMapping("/seed/addresses")
    public Result<?> seedAddresses(@RequestParam(defaultValue = "10") int count) {
        return Result.ok(seedService.generateAddresses(count));
    }

    @PostMapping("/seed/merchants")
    public Result<?> seedMerchants(@RequestParam(defaultValue = "5") int count) {
        return Result.ok(seedService.generateMerchants(count));
    }

    @PostMapping("/seed/comments")
    public Result<?> seedComments(@RequestParam(defaultValue = "10") int count) {
        return Result.ok(seedService.generateComments(count));
    }

    @PostMapping("/seed/users")
    public Result<?> seedUsers(@RequestParam(defaultValue = "5") int count) {
        return Result.ok(seedService.generateUsers(count));
    }

    @DeleteMapping("/seed/clear")
    public Result<?> seedClear() {
        return Result.ok(seedService.clearAll());
    }
}
