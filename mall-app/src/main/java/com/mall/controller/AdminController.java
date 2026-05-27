package com.mall.controller;

import com.mall.common.Result;
import com.mall.entity.Category;
import com.mall.entity.CategoryAttr;
import com.mall.entity.MallBanner;
import com.mall.entity.Notification;
import com.mall.entity.Product;
import com.mall.entity.ProductAttr;
import com.mall.service.AdminService;
import com.mall.service.BannerService;
import com.mall.service.CategoryService;
import com.mall.service.ChatService;
import com.mall.service.ComboService;
import com.mall.service.EvaluationService;
import com.mall.service.GoodsAttrService;
import com.mall.service.LoanService;
import com.mall.service.LotteryService;
import com.mall.service.SubscribeService;
import com.mall.service.SystemGoodsService;
import com.mall.service.AreaService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;

@RestController
@RequestMapping("/admin")
@RequiredArgsConstructor
public class AdminController {

    private final AdminService adminService;
    private final BannerService bannerService;
    private final CategoryService categoryService;
    private final EvaluationService evaluationService;
    private final ChatService chatService;
    private final GoodsAttrService goodsAttrService;
    private final ComboService comboService;
    private final LoanService loanService;
    private final LotteryService lotteryService;
    private final SubscribeService subscribeService;
    private final SystemGoodsService systemGoodsService;
    private final AreaService areaService;

    @PostMapping("/login")
    public Result<?> login(@RequestBody Map<String, String> dto) {
        return Result.ok(adminService.login(dto.get("username"), dto.get("password")));
    }

    @GetMapping("/dashboard")
    public Result<?> dashboard() {
        return Result.ok(adminService.dashboard());
    }

    @GetMapping("/user/list")
    public Result<?> userList(@RequestParam(required = false) String keyword,
                              @RequestParam(required = false) Integer status,
                              @RequestParam(defaultValue = "1") Integer pageNum,
                              @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.userList(keyword, status, pageNum, pageSize));
    }

    @PutMapping("/user/status")
    public Result<?> updateUserStatus(@RequestBody Map<String, Object> dto) {
        adminService.updateUserStatus(Long.valueOf(dto.get("userId").toString()),
            Integer.parseInt(dto.get("status").toString()));
        return Result.ok();
    }

    @PostMapping("/user/balance/adjust")
    public Result<?> adjustBalance(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        adminService.adjustBalance(Long.valueOf(dto.get("userId").toString()),
            new BigDecimal(dto.get("amount").toString()),
            dto.get("remark").toString(), userId);
        return Result.ok();
    }

    @GetMapping("/recharge/list")
    public Result<?> rechargeList(@RequestParam(defaultValue = "1") Integer pageNum,
                                  @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.rechargePending(pageNum, pageSize));
    }

    @PostMapping("/recharge/audit")
    public Result<?> auditRecharge(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        adminService.auditRecharge(Long.valueOf(dto.get("id").toString()),
            Boolean.parseBoolean(dto.get("approved").toString()),
            dto.get("reason") != null ? dto.get("reason").toString() : null, userId);
        return Result.ok();
    }

    @GetMapping("/withdraw/list")
    public Result<?> withdrawList(@RequestParam(defaultValue = "1") Integer pageNum,
                                  @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.withdrawPending(pageNum, pageSize));
    }

    @PostMapping("/withdraw/audit")
    public Result<?> auditWithdraw(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        adminService.auditWithdraw(Long.valueOf(dto.get("id").toString()),
            Boolean.parseBoolean(dto.get("approved").toString()),
            dto.get("txHash") != null ? dto.get("txHash").toString() : null,
            dto.get("reason") != null ? dto.get("reason").toString() : null, userId);
        return Result.ok();
    }

    @GetMapping("/merchant/apply/list")
    public Result<?> merchantApplyList(@RequestParam(defaultValue = "1") Integer pageNum,
                                       @RequestParam(defaultValue = "10") Integer pageSize) {
        return Result.ok(adminService.merchantApplyList(pageNum, pageSize));
    }

    @PostMapping("/merchant/apply/audit")
    public Result<?> auditMerchantApply(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        adminService.auditMerchantApply(Long.valueOf(dto.get("id").toString()),
            Boolean.parseBoolean(dto.get("approved").toString()),
            dto.get("reason") != null ? dto.get("reason").toString() : null, userId);
        return Result.ok();
    }

    @PostMapping("/order/refund/{id}")
    public Result<?> forceRefund(@RequestAttribute Long userId, @PathVariable Long id) {
        adminService.forceRefund(id, userId);
        return Result.ok();
    }

    @GetMapping("/product/list")
    public Result<?> productList(@RequestParam(required = false) String keyword,
                                  @RequestParam(required = false) Integer status,
                                  @RequestParam(defaultValue = "1") Integer page,
                                  @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(adminService.productList(keyword, status, page, pageSize));
    }

    @PostMapping("/product/audit")
    public Result<?> auditProduct(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        adminService.auditProduct(Long.valueOf(dto.get("productId").toString()),
            Integer.parseInt(dto.get("status").toString()), userId);
        return Result.ok();
    }

    @GetMapping("/product/{id}")
    public Result<?> productDetail(@PathVariable Long id) {
        return Result.ok(adminService.productDetail(id));
    }

    @PutMapping("/product/{id}")
    public Result<?> productUpdate(@PathVariable Long id, @RequestBody Product product) {
        adminService.productUpdate(id, product);
        return Result.ok();
    }

    @DeleteMapping("/product/{id}")
    public Result<?> productDelete(@PathVariable Long id) {
        adminService.productDelete(id);
        return Result.ok();
    }

    @PostMapping("/product")
    public Result<?> productCreate(@RequestBody Product product) {
        adminService.productCreate(product);
        return Result.ok();
    }

    @PutMapping("/product/{id}/status")
    public Result<?> productUpdateStatus(@PathVariable Long id, @RequestBody Map<String, Object> dto) {
        adminService.productUpdateStatus(id, Integer.parseInt(dto.get("status").toString()));
        return Result.ok();
    }

    @GetMapping("/merchant/list")
    public Result<?> merchantList(@RequestParam(required = false) String keyword,
                                   @RequestParam(required = false) Integer status,
                                   @RequestParam(defaultValue = "1") Integer page,
                                   @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(adminService.merchantList(keyword, status, page, pageSize));
    }

    @PutMapping("/merchant/status")
    public Result<?> updateMerchantStatus(@RequestBody Map<String, Object> dto) {
        adminService.updateMerchantStatus(Long.valueOf(dto.get("merchantId").toString()),
            Integer.parseInt(dto.get("status").toString()));
        return Result.ok();
    }

    @GetMapping("/order/list")
    public Result<?> orderList(@RequestParam(required = false) String keyword,
                                @RequestParam(required = false) Integer status,
                                @RequestParam(defaultValue = "1") Integer page,
                                @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(adminService.orderList(keyword, status, page, pageSize));
    }

    @GetMapping("/order/{id}")
    public Result<?> orderDetail(@PathVariable Long id) {
        return Result.ok(adminService.orderDetail(id));
    }

    @PutMapping("/order/{id}/status")
    public Result<?> orderUpdateStatus(@PathVariable Long id, @RequestBody Map<String, Object> dto) {
        adminService.updateOrderStatus(id, Integer.parseInt(dto.get("status").toString()));
        return Result.ok();
    }

    // === 轮播管理 ===

    @GetMapping("/banner/list")
    public Result<?> bannerList(@RequestParam(required = false) String type,
                                 @RequestParam(required = false) String startTime,
                                 @RequestParam(required = false) String endTime,
                                 @RequestParam(defaultValue = "1") Integer page,
                                 @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(bannerService.list(type, null, startTime, endTime, page, pageSize));
    }

    @GetMapping("/banner/{uuid}")
    public Result<?> bannerDetail(@PathVariable String uuid) {
        MallBanner banner = bannerService.getById(uuid);
        if (banner == null) {
            return Result.fail("轮播图不存在");
        }
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

    // === 分类管理 ===

    @GetMapping("/category/list")
    public Result<?> categoryList(@RequestParam(required = false) String parentId,
                                   @RequestParam(required = false) Integer level,
                                   @RequestParam(required = false) String startTime,
                                   @RequestParam(required = false) String endTime,
                                   @RequestParam(defaultValue = "1") Integer page,
                                   @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(categoryService.list(parentId, level, startTime, endTime, page, pageSize));
    }

    @GetMapping("/category/all")
    public Result<?> categoryAll() {
        return Result.ok(categoryService.listAll());
    }

    @GetMapping("/category/{uuid}")
    public Result<?> categoryDetail(@PathVariable String uuid) {
        Category category = categoryService.getById(uuid);
        if (category == null) {
            return Result.fail("分类不存在");
        }
        return Result.ok(category);
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

    // === 评价管理 ===

    @GetMapping("/evaluation/list")
    public Result<?> evaluationList(@RequestParam(required = false) String keyword,
                                     @RequestParam(required = false) Integer status,
                                     @RequestParam(defaultValue = "1") Integer page,
                                     @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(evaluationService.adminList(keyword, status, page, pageSize));
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

    // === 客服管理 ===

    @GetMapping("/chat/conversations")
    public Result<?> chatConversations(@RequestParam(defaultValue = "1") Integer page,
                                        @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(chatService.adminConversations(page, pageSize));
    }

    @GetMapping("/chat/messages/{conversationId}")
    public Result<?> chatMessages(@PathVariable String conversationId) {
        return Result.ok(chatService.adminMessages(conversationId));
    }

    @PostMapping("/chat/reply/{conversationId}")
    public Result<?> chatReply(@PathVariable String conversationId, @RequestBody Map<String, String> dto) {
        return Result.ok(chatService.adminReply(conversationId, dto.get("content")));
    }

    // === 属性分类管理 ===

    @GetMapping("/attr-category/list")
    public Result<?> attrCategoryList(@RequestParam(required = false) String keyword,
                                       @RequestParam(defaultValue = "1") Integer page,
                                       @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(goodsAttrService.categoryList(keyword, page, pageSize));
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

    // === 属性管理 ===

    @GetMapping("/attr/list")
    public Result<?> attrList(@RequestParam(required = false) String categoryId,
                               @RequestParam(defaultValue = "1") Integer page,
                               @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(goodsAttrService.attrList(categoryId, page, pageSize));
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

    // === 属性值管理 ===

    @GetMapping("/attr-value/list")
    public Result<?> attrValueList(@RequestParam String attrId,
                                    @RequestParam(defaultValue = "1") Integer page,
                                    @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(goodsAttrService.valueList(attrId, page, pageSize));
    }

    @GetMapping("/attr-value/{id}")
    public Result<?> attrValueDetail(@PathVariable String id) {
        return Result.ok(goodsAttrService.valueGetById(id));
    }

    @PostMapping("/attr-value")
    public Result<?> attrValueSave(@RequestBody Map<String, String> dto) {
        goodsAttrService.valueSave(dto.get("attrId"), dto.get("name"), dto.get("lang"));
        return Result.ok();
    }

    @PutMapping("/attr-value/{id}")
    public Result<?> attrValueUpdate(@PathVariable String id, @RequestBody Map<String, String> dto) {
        goodsAttrService.valueUpdate(id, dto.get("name"), dto.get("lang"));
        return Result.ok();
    }

    @DeleteMapping("/attr-value/{id}")
    public Result<?> attrValueDelete(@PathVariable String id) {
        goodsAttrService.valueDelete(id);
        return Result.ok();
    }

    // ======================== 代理管理 ========================

    /** 代理列表 */
    @GetMapping("/agent/list")
    public Result<?> agentList(@RequestParam(required = false) String keyword,
                                @RequestParam(required = false) String level,
                                @RequestParam(required = false) Integer status,
                                @RequestParam(defaultValue = "1") Integer page,
                                @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(adminService.agentList(keyword, level, status, page, pageSize));
    }

    /** 代理详情 */
    @GetMapping("/agent/{sellerId}")
    public Result<?> agentDetail(@PathVariable String sellerId) {
        return Result.ok(adminService.agentDetail(sellerId));
    }

    /** 启用/禁用代理 */
    @PutMapping("/agent/{sellerId}/status")
    public Result<?> agentUpdateStatus(@PathVariable String sellerId, @RequestBody Map<String, Object> dto) {
        adminService.updateAgentStatus(sellerId, Integer.parseInt(dto.get("status").toString()));
        return Result.ok();
    }

    /** 代理下级团队 */
    @GetMapping("/agent/{sellerId}/team")
    public Result<?> agentTeam(@PathVariable String sellerId,
                                @RequestParam(defaultValue = "1") Integer page,
                                @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(adminService.agentTeam(sellerId, page, pageSize));
    }

    /** 代理等级列表 */
    @GetMapping("/agent/level/list")
    public Result<?> agentLevelList() {
        return Result.ok(adminService.agentLevelList());
    }

    /** 新增/修改代理等级 */
    @PostMapping("/agent/level")
    public Result<?> agentLevelSave(@RequestBody Map<String, Object> dto) {
        adminService.agentLevelSave(dto);
        return Result.ok();
    }

    /** 删除代理等级 */
    @DeleteMapping("/agent/level/{uuid}")
    public Result<?> agentLevelDelete(@PathVariable String uuid) {
        adminService.agentLevelDelete(uuid);
        return Result.ok();
    }

    /** 返利记录列表 */
    @GetMapping("/agent/rebate/list")
    public Result<?> agentRebateList(@RequestParam(required = false) String keyword,
                                      @RequestParam(required = false) String level,
                                      @RequestParam(required = false) String startDate,
                                      @RequestParam(required = false) String endDate,
                                      @RequestParam(defaultValue = "1") Integer page,
                                      @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(adminService.agentRebateList(keyword, level, startDate, endDate, page, pageSize));
    }

    /** 返利统计 */
    @GetMapping("/agent/rebate/stats")
    public Result<?> agentRebateStats() {
        return Result.ok(adminService.agentRebateStats());
    }

    // === 通知管理 ===

    @GetMapping("/notification/list")
    public Result<?> notificationList(@RequestParam(defaultValue = "1") Integer page,
                                       @RequestParam(defaultValue = "20") Integer pageSize,
                                       @RequestParam(required = false) String type,
                                       @RequestParam(required = false) String keyword) {
        return Result.ok(adminService.notificationList(page, pageSize, type, keyword));
    }

    @PutMapping("/notification/{id}")
    public Result<?> notificationUpdate(@PathVariable Long id, @RequestBody Notification notification) {
        adminService.notificationUpdate(id, notification);
        return Result.ok();
    }

    @DeleteMapping("/notification/{id}")
    public Result<?> notificationDelete(@PathVariable Long id) {
        adminService.notificationAdminDelete(id);
        return Result.ok();
    }

    // === 套餐管理 ===

    @GetMapping("/combo/list")
    public Result<?> comboList(@RequestParam(required = false) String name,
                                @RequestParam(required = false) String startTime,
                                @RequestParam(required = false) String endTime,
                                @RequestParam(defaultValue = "1") Integer page,
                                @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(comboService.adminComboList(name, startTime, endTime, page, pageSize));
    }

    @PostMapping("/combo")
    public Result<?> comboSave(@RequestBody Map<String, Object> dto) {
        comboService.adminComboSave(
            (String) dto.get("name"),
            (String) dto.get("iconImg"),
            dto.get("amount") != null ? new BigDecimal(dto.get("amount").toString()) : null,
            dto.get("day") != null ? Integer.valueOf(dto.get("day").toString()) : null,
            dto.get("promoteNum") != null ? Integer.valueOf(dto.get("promoteNum").toString()) : null,
            dto.get("baseAccessNum") != null ? Integer.valueOf(dto.get("baseAccessNum").toString()) : null,
            dto.get("autoAccMin") != null ? Integer.valueOf(dto.get("autoAccMin").toString()) : null,
            dto.get("autoAccMax") != null ? Integer.valueOf(dto.get("autoAccMax").toString()) : null
        );
        return Result.ok();
    }

    @PutMapping("/combo/{uuid}")
    public Result<?> comboUpdate(@PathVariable String uuid, @RequestBody Map<String, Object> dto) {
        comboService.adminComboUpdate(uuid,
            (String) dto.get("name"),
            (String) dto.get("iconImg"),
            dto.get("amount") != null ? new BigDecimal(dto.get("amount").toString()) : null,
            dto.get("day") != null ? Integer.valueOf(dto.get("day").toString()) : null,
            dto.get("promoteNum") != null ? Integer.valueOf(dto.get("promoteNum").toString()) : null,
            dto.get("baseAccessNum") != null ? Integer.valueOf(dto.get("baseAccessNum").toString()) : null,
            dto.get("autoAccMin") != null ? Integer.valueOf(dto.get("autoAccMin").toString()) : null,
            dto.get("autoAccMax") != null ? Integer.valueOf(dto.get("autoAccMax").toString()) : null
        );
        return Result.ok();
    }

    @DeleteMapping("/combo/{uuid}")
    public Result<?> comboDelete(@PathVariable String uuid) {
        comboService.adminComboDelete(uuid);
        return Result.ok();
    }

    @GetMapping("/combo/record/list")
    public Result<?> comboRecordList(@RequestParam(required = false) String userCode,
                                      @RequestParam(required = false) String sellerName,
                                      @RequestParam(required = false) String startTime,
                                      @RequestParam(required = false) String endTime,
                                      @RequestParam(defaultValue = "1") Integer page,
                                      @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(comboService.adminComboRecordList(userCode, sellerName, startTime, endTime, page, pageSize));
    }

    // === 安全重置审核（窗口3） ===

    /** 安全重置申请列表 */
    @GetMapping("/safeword/list")
    public Result<?> safewordApplyList(@RequestParam(defaultValue = "1") Integer page,
                                       @RequestParam(defaultValue = "20") Integer pageSize,
                                       @RequestParam(required = false) String keyword,
                                       @RequestParam(required = false) Integer status,
                                       @RequestParam(required = false) Integer operate) {
        return Result.ok(adminService.safewordApplyList(page, pageSize, keyword, status, operate));
    }

    /** 通过安全重置申请 */
    @PostMapping("/safeword/{id}/approve")
    public Result<?> safewordApprove(@RequestAttribute Long userId, @PathVariable Long id,
                                     @RequestBody Map<String, String> body) {
        String safeword = body.get("safeword");
        if (safeword == null || safeword.isEmpty()) return Result.fail("请输入管理员资金密码");
        adminService.safewordApprove(id, userId, safeword);
        return Result.ok();
    }

    /** 拒绝安全重置申请 */
    @PostMapping("/safeword/{id}/reject")
    public Result<?> safewordReject(@RequestAttribute Long userId, @PathVariable Long id,
                                    @RequestBody Map<String, String> body) {
        String msg = body.get("msg");
        if (msg == null || msg.isEmpty()) return Result.fail("请输入拒绝原因");
        adminService.safewordReject(id, userId, msg);
        return Result.ok();
    }

    // ======================== 贷款审核管理 ========================

    @GetMapping("/loan/list")
    public Result<?> loanList(@RequestParam(required = false) String keyword,
                               @RequestParam(required = false) Integer status,
                               @RequestParam(defaultValue = "1") Integer page,
                               @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(loanService.adminList(keyword, status, page, pageSize));
    }

    @PostMapping("/loan/audit")
    public Result<?> loanAudit(@RequestAttribute Long userId, @RequestBody Map<String, Object> dto) {
        loanService.audit(userId, dto.get("uuid").toString(), dto);
        return Result.ok();
    }

    @GetMapping("/loan/config")
    public Result<?> loanConfigList() {
        return Result.ok(loanService.configList());
    }

    @PostMapping("/loan/config")
    public Result<?> loanConfigSave(@RequestBody Map<String, Object> dto) {
        loanService.saveConfig(dto);
        return Result.ok();
    }

    // ======================== 活动抽奖配置管理 ========================

    @GetMapping("/activity/list")
    public Result<?> activityList(@RequestParam(required = false) String keyword,
                                    @RequestParam(required = false) Integer status,
                                    @RequestParam(defaultValue = "1") Integer page,
                                    @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(lotteryService.adminActivityList(keyword, status, page, pageSize));
    }

    @GetMapping("/activity/{id}")
    public Result<?> activityDetail(@PathVariable String id) {
        return Result.ok(lotteryService.adminActivityDetail(id));
    }

    @PostMapping("/activity")
    public Result<?> activitySave(@RequestBody Map<String, Object> dto) {
        lotteryService.adminActivitySave(dto);
        return Result.ok();
    }

    @PutMapping("/activity/{id}")
    public Result<?> activityUpdate(@PathVariable String id, @RequestBody Map<String, Object> dto) {
        dto.put("id", id);
        lotteryService.adminActivityUpdate(dto);
        return Result.ok();
    }

    @PutMapping("/activity/{id}/show")
    public Result<?> activityToggleShow(@PathVariable String id, @RequestBody Map<String, Object> dto) {
        lotteryService.adminActivityToggleShow(id, Integer.parseInt(dto.get("isShow").toString()));
        return Result.ok();
    }

    @DeleteMapping("/activity/{id}")
    public Result<?> activityDelete(@PathVariable String id) {
        lotteryService.adminActivityDelete(id);
        return Result.ok();
    }

    @GetMapping("/activity/{id}/prize/list")
    public Result<?> activityPrizeList(@PathVariable String id) {
        return Result.ok(lotteryService.adminPrizeListByActivity(id));
    }

    @PostMapping("/activity/prize")
    public Result<?> activityPrizeSave(@RequestBody Map<String, Object> dto) {
        lotteryService.adminPrizeSave(dto);
        return Result.ok();
    }

    @PutMapping("/activity/prize/{prizeId}")
    public Result<?> activityPrizeUpdate(@PathVariable String prizeId, @RequestBody Map<String, Object> dto) {
        dto.put("id", prizeId);
        lotteryService.adminPrizeUpdate(dto);
        return Result.ok();
    }

    @DeleteMapping("/activity/prize/{prizeId}")
    public Result<?> activityPrizeDelete(@PathVariable String prizeId) {
        lotteryService.adminPrizeDelete(prizeId);
        return Result.ok();
    }

    @GetMapping("/activity/record/list")
    public Result<?> activityRecordList(@RequestParam(required = false) String username,
                                         @RequestParam(required = false) Integer prizeType,
                                         @RequestParam(required = false) String startTime,
                                         @RequestParam(required = false) String endTime,
                                         @RequestParam(defaultValue = "1") Integer page,
                                         @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(lotteryService.adminRecordList(username, prizeType, startTime, endTime, page, pageSize));
    }

    // ======================== 区域管理 ========================

    @GetMapping("/area/country/list")
    public Result<?> countryList(@RequestParam(required = false) String countryName,
                                   @RequestParam(required = false) Integer flag,
                                   @RequestParam(defaultValue = "1") Integer page,
                                   @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(areaService.countryList(countryName, flag, page, pageSize));
    }

    @PostMapping("/area/country")
    public Result<?> countrySave(@RequestBody Map<String, Object> dto) {
        areaService.countrySave(dto);
        return Result.ok();
    }

    @PutMapping("/area/country/{id}")
    public Result<?> countryUpdate(@PathVariable Long id, @RequestBody Map<String, Object> dto) {
        areaService.countryUpdate(id, dto);
        return Result.ok();
    }

    @DeleteMapping("/area/country/{id}")
    public Result<?> countryDelete(@PathVariable Long id) {
        areaService.countryDelete(id);
        return Result.ok();
    }

    @GetMapping("/area/city/list")
    public Result<?> cityList(@RequestParam(required = false) String cityName,
                                @RequestParam(required = false) Long countryId,
                                @RequestParam(required = false) Integer flag,
                                @RequestParam(defaultValue = "1") Integer page,
                                @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(areaService.cityList(cityName, countryId, flag, page, pageSize));
    }

    @PostMapping("/area/city")
    public Result<?> citySave(@RequestBody Map<String, Object> dto) {
        areaService.citySave(dto);
        return Result.ok();
    }

    @PutMapping("/area/city/{id}")
    public Result<?> cityUpdate(@PathVariable Long id, @RequestBody Map<String, Object> dto) {
        areaService.cityUpdate(id, dto);
        return Result.ok();
    }

    @DeleteMapping("/area/city/{id}")
    public Result<?> cityDelete(@PathVariable Long id) {
        areaService.cityDelete(id);
        return Result.ok();
    }

    // ======================== 订阅推送管理 ========================

    @GetMapping("/subscribe/list")
    public Result<?> subscribeList(@RequestParam(required = false) String email,
                                     @RequestParam(required = false) String startTime,
                                     @RequestParam(required = false) String endTime,
                                     @RequestParam(defaultValue = "1") Integer page,
                                     @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(subscribeService.adminList(email, startTime, endTime, page, pageSize));
    }

    @DeleteMapping("/subscribe/{id}")
    public Result<?> subscribeDelete(@PathVariable Long id) {
        subscribeService.adminDelete(id);
        return Result.ok();
    }

    @PostMapping("/subscribe/push")
    public Result<?> subscribePush(@RequestBody Map<String, Object> dto) {
        subscribeService.adminPush(dto);
        return Result.ok();
    }

    // ======================== 系统商品库管理 ========================

    @GetMapping("/goods-library/list")
    public Result<?> goodsLibraryList(@RequestParam(required = false) String name,
                                        @RequestParam(required = false) String categoryId,
                                        @RequestParam(required = false) Integer isShelf,
                                        @RequestParam(required = false) Integer updateStatus,
                                        @RequestParam(defaultValue = "1") Integer page,
                                        @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(systemGoodsService.adminList(name, categoryId, isShelf, updateStatus, page, pageSize));
    }

    @GetMapping("/goods-library/{id}")
    public Result<?> goodsLibraryDetail(@PathVariable String id,
                                         @RequestParam(defaultValue = "cn") String lang) {
        return Result.ok(systemGoodsService.adminDetail(id, lang));
    }

    @PostMapping("/goods-library")
    public Result<?> goodsLibrarySave(@RequestBody Map<String, Object> dto) {
        systemGoodsService.adminSave(dto);
        return Result.ok();
    }

    @PutMapping("/goods-library/{id}")
    public Result<?> goodsLibraryUpdate(@PathVariable String id, @RequestBody Map<String, Object> dto) {
        dto.put("id", id);
        systemGoodsService.adminUpdate(dto);
        return Result.ok();
    }

    @DeleteMapping("/goods-library/{id}")
    public Result<?> goodsLibraryDelete(@PathVariable String id) {
        systemGoodsService.adminDelete(id);
        return Result.ok();
    }

    @PutMapping("/goods-library/{id}/shelf")
    public Result<?> goodsLibraryShelf(@PathVariable String id, @RequestBody Map<String, Object> dto) {
        systemGoodsService.adminUpdateShelf(id, Integer.parseInt(dto.get("isShelf").toString()));
        return Result.ok();
    }

    @DeleteMapping("/goods-library/sku/{skuId}")
    public Result<?> goodsLibraryDeleteSku(@PathVariable String skuId) {
        systemGoodsService.deleteSku(skuId);
        return Result.ok();
    }

    // ======================== 系统评论管理（旧AdminSystemGoodsController/AdminSystemCommentController） ========================

    @GetMapping("/system-comment/list")
    public Result<?> systemCommentList(@RequestParam(required = false) String systemGoodsId,
                                        @RequestParam(required = false) Integer status,
                                        @RequestParam(defaultValue = "1") Integer page,
                                        @RequestParam(defaultValue = "20") Integer pageSize) {
        return Result.ok(evaluationService.systemCommentList(systemGoodsId, status, page, pageSize));
    }

    @PostMapping("/system-comment")
    public Result<?> systemCommentSave(@RequestBody Map<String, Object> dto) {
        evaluationService.systemCommentSave(dto);
        return Result.ok();
    }

    @PutMapping("/system-comment/{id}/status")
    public Result<?> systemCommentUpdateStatus(@PathVariable String id, @RequestBody Map<String, Object> dto) {
        evaluationService.systemCommentUpdateStatus(id, Integer.parseInt(dto.get("status").toString()));
        return Result.ok();
    }

    @DeleteMapping("/system-comment/{id}")
    public Result<?> systemCommentDelete(@PathVariable String id) {
        evaluationService.systemCommentDelete(id);
        return Result.ok();
    }
}
