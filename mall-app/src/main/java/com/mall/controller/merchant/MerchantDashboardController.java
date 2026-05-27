package com.mall.controller.merchant;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.mall.common.Result;
import com.mall.entity.*;
import com.mall.mapper.*;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 商家端-仪表盘（迁移自旧商城 SellerInstrumentPanelController）
 * 增强版仪表盘：头部/趋势折线/热销商品/订单状态分布
 */
@RestController
@RequestMapping("/merchant")
@RequiredArgsConstructor
public class MerchantDashboardController {

    private final MallOrdersPrizeMapper ordersPrizeMapper;
    private final MallOrdersGoodsMapper ordersGoodsMapper;
    private final MallSellerMapper sellerMapper;
    private final MallEvaluationMapper evaluationMapper;
    private final MallFocusSellerMapper focusSellerMapper;
    private final ProductMapper productMapper;
    private final MerchantMapper merchantMapper;
    private final KycMapper kycMapper;

    /**
     * 仪表盘头部（含商品数/销售额/订单数/利润/信誉分/关注数/评分/认证状态）
     */
    @GetMapping("/instrument-panel/head")
    public Result<?> dashboardHead(@RequestAttribute Long userId) {
        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        String sellerId = String.valueOf(merchant.getUserId());
        Map<String, Object> head = new HashMap<>();

        // 商品数量
        QueryWrapper<Product> productQw = new QueryWrapper<>();
        productQw.eq("merchant_id", userId).eq("deleted", 0);
        head.put("goodsNum", productMapper.selectCount(productQw));

        // 总销售额 & 订单数（从mall_orders_prize统计）
        QueryWrapper<MallOrdersPrize> totalQw = new QueryWrapper<>();
        totalQw.eq("seller_id", sellerId);
        List<MallOrdersPrize> allOrders = ordersPrizeMapper.selectList(totalQw);

        double totalSales = allOrders.stream()
                .mapToDouble(o -> o.getPrizeReal() != null ? o.getPrizeReal() : 0).sum();
        head.put("totalSales", totalSales);
        head.put("orderNum", allOrders.size());

        // 总利润
        double totalProfit = allOrders.stream()
                .mapToDouble(o -> o.getProfit() != null ? o.getProfit() : 0).sum();
        head.put("totalProfit", totalProfit);

        // 店铺信誉分 from mall_seller
        MallSeller seller = sellerMapper.selectById(sellerId);
        head.put("creditScore", seller != null ? seller.getCreditScore() : 0);

        // 关注数
        QueryWrapper<MallFocusSeller> focusQw = new QueryWrapper<>();
        focusQw.eq("seller_id", sellerId);
        head.put("focusCount", focusSellerMapper.selectCount(focusQw));

        // 评分
        QueryWrapper<MallEvaluation> evalQw = new QueryWrapper<>();
        evalQw.eq("seller_id", sellerId);
        List<MallEvaluation> evals = evaluationMapper.selectList(evalQw);
        double avgRating = evals.stream()
                .mapToInt(e -> e.getRating() != null ? e.getRating() : 0).average().orElse(0);
        head.put("rating", Math.round(avgRating * 10.0) / 10.0);

        // 今日新增订单
        String today = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        QueryWrapper<MallOrdersPrize> todayOrderQw = new QueryWrapper<>();
        todayOrderQw.eq("seller_id", sellerId);
        todayOrderQw.apply("DATE(create_time) = {0}", today);
        List<MallOrdersPrize> todayOrders = ordersPrizeMapper.selectList(todayOrderQw);
        head.put("todayOrder", todayOrders.size());

        // 今日销售额
        double todaySales = todayOrders.stream()
                .mapToDouble(o -> o.getPrizeReal() != null ? o.getPrizeReal() : 0).sum();
        head.put("todaySales", todaySales);

        // 今日利润
        double todayProfit = todayOrders.stream()
                .mapToDouble(o -> o.getProfit() != null ? o.getProfit() : 0).sum();
        head.put("todayProfit", todayProfit);

        // 店铺认证状态: 0-未认证 1-完成基础设置 2-KYC已通过 3-已上架商品
        head.put("freeze", seller != null ? seller.getStatus() : 0);

        QueryWrapper<Kyc> kycQw = new QueryWrapper<>();
        kycQw.eq("user_id", merchant.getUserId());
        Kyc kyc = kycMapper.selectOne(kycQw);

        if (kyc == null || kyc.getRealName() == null || kyc.getRealName().isBlank()) {
            head.put("storeCheckState", 0);
        } else if (kyc.getStatus() != null && kyc.getStatus() == 1) {
            QueryWrapper<Product> activeQw = new QueryWrapper<Product>()
                    .eq("merchant_id", userId).eq("deleted", 0).eq("status", 1);
            Long goodsCount = productMapper.selectCount(activeQw);
            head.put("storeCheckState", goodsCount > 0 ? 3 : 2);
        } else {
            head.put("storeCheckState", 1);
        }

        return Result.ok(Map.of("head", head));
    }

    /**
     * 趋势折线图数据（天/周/月）
     * type: 0=today, 1=last7days, 2=thisMonth
     */
    @GetMapping("/instrument-panel/line")
    public Result<?> trendLine(@RequestAttribute Long userId,
                               @RequestParam(defaultValue = "2") Integer type) {
        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        String sellerId = String.valueOf(merchant.getUserId());
        String startTime;
        String endTime = LocalDate.now().plusDays(1).format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));

        startTime = switch (type) {
            case 0 -> LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            case 1 -> LocalDate.now().minusDays(7).format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            default -> LocalDate.now().withDayOfMonth(1).format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        };

        QueryWrapper<MallOrdersPrize> qw = new QueryWrapper<>();
        qw.eq("seller_id", sellerId);
        qw.between("create_time", startTime + " 00:00:00", endTime + " 00:00:00");
        qw.orderByAsc("create_time");
        List<MallOrdersPrize> orders = ordersPrizeMapper.selectList(qw);

        // Group by day
        Map<String, List<MallOrdersPrize>> grouped = orders.stream()
                .filter(o -> o.getCreateTime() != null)
                .collect(Collectors.groupingBy(
                        o -> o.getCreateTime().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")),
                        LinkedHashMap::new, Collectors.toList()));

        List<Map<String, Object>> line = new ArrayList<>();
        for (Map.Entry<String, List<MallOrdersPrize>> entry : grouped.entrySet()) {
            Map<String, Object> point = new HashMap<>();
            point.put("dayString", entry.getKey());
            point.put("countSales", entry.getValue().stream()
                    .mapToDouble(o -> o.getPrizeReal() != null ? o.getPrizeReal() : 0).sum());
            point.put("countOrders", entry.getValue().size());
            line.add(point);
        }

        return Result.ok(Map.of("line", line));
    }

    /**
     * 热销商品排行（Top10 by sales）
     */
    @GetMapping("/instrument-panel/top-goods")
    public Result<?> topGoods(@RequestAttribute Long userId) {
        QueryWrapper<Product> qw = new QueryWrapper<>();
        qw.eq("merchant_id", userId);
        qw.eq("deleted", 0);
        qw.orderByDesc("sales");
        qw.last("LIMIT 10");

        List<Product> products = productMapper.selectList(qw);
        List<Map<String, Object>> list = products.stream().map(p -> {
            Map<String, Object> m = new HashMap<>();
            m.put("id", p.getId());
            m.put("name", p.getName());
            m.put("mainImage", p.getMainImage());
            m.put("price", p.getPrice());
            m.put("sales", p.getSales());
            m.put("status", p.getStatus());
            return m;
        }).collect(Collectors.toList());

        return Result.ok(Map.of("goods", list));
    }

    /**
     * 订单状态分布统计
     */
    @GetMapping("/instrument-panel/stats")
    public Result<?> orderStats(@RequestAttribute Long userId) {
        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        String sellerId = String.valueOf(merchant.getUserId());

        QueryWrapper<MallOrdersPrize> allQw = new QueryWrapper<>();
        allQw.eq("seller_id", sellerId);
        Long totalOrders = ordersPrizeMapper.selectCount(allQw);

        QueryWrapper<MallOrdersPrize> ingQw = new QueryWrapper<>();
        ingQw.eq("seller_id", sellerId);
        ingQw.in("status", Arrays.asList(0, 2));
        Long orderIng = ordersPrizeMapper.selectCount(ingQw);

        QueryWrapper<MallOrdersPrize> finishQw = new QueryWrapper<>();
        finishQw.eq("seller_id", sellerId);
        finishQw.eq("status", 4);
        Long orderFinish = ordersPrizeMapper.selectCount(finishQw);

        QueryWrapper<MallOrdersPrize> cancelQw = new QueryWrapper<>();
        cancelQw.eq("seller_id", sellerId);
        cancelQw.eq("status", 7);
        Long orderCancel = ordersPrizeMapper.selectCount(cancelQw);

        Map<String, Object> stats = new HashMap<>();
        stats.put("orderNum", totalOrders);
        stats.put("orderIng", orderIng);
        stats.put("orderFinish", orderFinish);
        stats.put("orderCancel", orderCancel);

        return Result.ok(Map.of("stats", stats));
    }
}
