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
 * 商家端-财务报表（迁移自旧商城 SellerReportController）
 * 提供收入/利润/订单统计头部摘要 和 按日期的报表明细列表
 */
@RestController
@RequestMapping("/merchant")
@RequiredArgsConstructor
public class MerchantFinanceController {

    private final MallOrdersPrizeMapper ordersPrizeMapper;
    private final MerchantMapper merchantMapper;

    /**
     * 财务报表头部摘要
     * contentType: 0=today, 1=last7days, 2=thisMonth, 3=all
     */
    @GetMapping("/finance-report/head")
    public Result<?> financeHead(@RequestAttribute Long userId,
                                 @RequestParam(defaultValue = "0") Integer contentType) {

        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        String sellerId = String.valueOf(merchant.getUserId());
        String startTime = getStartTime(contentType);
        String endTime = LocalDate.now().plusDays(1).format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));

        // Base query with time filter
        QueryWrapper<MallOrdersPrize> baseQw = new QueryWrapper<>();
        baseQw.eq("seller_id", sellerId);
        if (startTime != null) baseQw.ge("create_time", startTime + " 00:00:00");
        baseQw.le("create_time", endTime + " 00:00:00");

        List<MallOrdersPrize> filteredOrders = ordersPrizeMapper.selectList(baseQw);

        // TotalSales
        BigDecimal totalSales = filteredOrders.stream()
                .map(o -> o.getPrizeReal() != null ? BigDecimal.valueOf(o.getPrizeReal()) : BigDecimal.ZERO)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        // TotalProfit
        BigDecimal totalProfit = filteredOrders.stream()
                .map(o -> o.getProfit() != null ? BigDecimal.valueOf(o.getProfit()) : BigDecimal.ZERO)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        // OrderNum
        long orderNum = filteredOrders.size();

        // OrderReturns
        long orderReturns = filteredOrders.stream()
                .filter(o -> o.getReturnStatus() != null && o.getReturnStatus() > 0).count();

        // OrderCancel
        long orderCancel = filteredOrders.stream()
                .filter(o -> o.getStatus() != null && o.getStatus() == 7).count();

        // WillIncome (unsettled profit)
        QueryWrapper<MallOrdersPrize> willIncomeQw = new QueryWrapper<>();
        willIncomeQw.eq("seller_id", sellerId);
        willIncomeQw.eq("profit_status", 0);
        willIncomeQw.in("status", Arrays.asList(2, 4));
        List<MallOrdersPrize> unsettledOrders = ordersPrizeMapper.selectList(willIncomeQw);
        BigDecimal willIncome = unsettledOrders.stream()
                .map(o -> o.getProfit() != null ? BigDecimal.valueOf(o.getProfit()) : BigDecimal.ZERO)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        Map<String, Object> head = new HashMap<>();
        head.put("willIncome", willIncome);
        head.put("totalSales", totalSales);
        head.put("totalProfit", totalProfit);
        head.put("orderNum", orderNum);
        head.put("orderReturns", orderReturns);
        head.put("orderCancel", orderCancel);

        return Result.ok(Map.of("head", head));
    }

    /**
     * 财务报表列表（按日期分组）
     * contentType: 0=today, 1=last7days, 2=thisMonth
     */
    @GetMapping("/finance-report/list")
    public Result<?> financeList(@RequestAttribute Long userId,
                                  @RequestParam(defaultValue = "2") Integer contentType,
                                  @RequestParam(defaultValue = "1") Integer pageNum,
                                  @RequestParam(defaultValue = "31") Integer pageSize) {

        Merchant merchant = merchantMapper.selectById(userId);
        if (merchant == null) return Result.fail("商家不存在");

        String sellerId = String.valueOf(merchant.getUserId());
        String startTime = getStartTime(contentType);
        String endTime = LocalDate.now().plusDays(1).format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));

        QueryWrapper<MallOrdersPrize> qw = new QueryWrapper<>();
        qw.eq("seller_id", sellerId);
        if (startTime != null) qw.ge("create_time", startTime + " 00:00:00");
        qw.le("create_time", endTime + " 00:00:00");
        qw.orderByDesc("create_time");

        List<MallOrdersPrize> allOrders = ordersPrizeMapper.selectList(qw);

        // Group by day (yyyy-MM-dd)
        Map<String, List<MallOrdersPrize>> grouped = allOrders.stream()
                .filter(o -> o.getCreateTime() != null)
                .collect(Collectors.groupingBy(
                        o -> o.getCreateTime().toLocalDate().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")),
                        LinkedHashMap::new, Collectors.toList()));

        List<Map<String, Object>> reportList = new ArrayList<>();
        for (Map.Entry<String, List<MallOrdersPrize>> entry : grouped.entrySet()) {
            String day = entry.getKey();
            List<MallOrdersPrize> dayOrders = entry.getValue();

            Map<String, Object> row = new HashMap<>();
            row.put("dayString", day);
            row.put("orderNum", (long) dayOrders.size());
            row.put("totalSales", dayOrders.stream()
                    .map(o -> o.getPrizeReal() != null ? BigDecimal.valueOf(o.getPrizeReal()) : BigDecimal.ZERO)
                    .reduce(BigDecimal.ZERO, BigDecimal::add));
            row.put("totalProfit", dayOrders.stream()
                    .map(o -> o.getProfit() != null ? BigDecimal.valueOf(o.getProfit()) : BigDecimal.ZERO)
                    .reduce(BigDecimal.ZERO, BigDecimal::add));
            row.put("orderReturns", dayOrders.stream()
                    .filter(o -> o.getReturnStatus() != null && o.getReturnStatus() > 0).count());
            row.put("orderCancel", dayOrders.stream()
                    .filter(o -> o.getStatus() != null && o.getStatus() == 7).count());

            reportList.add(row);
        }

        // Manual pagination of grouped results
        int start = (pageNum - 1) * pageSize;
        int end = Math.min(start + pageSize, reportList.size());
        List<Map<String, Object>> pagedList = start < reportList.size() ?
                reportList.subList(start, end) : Collections.emptyList();

        Map<String, Object> data = new HashMap<>();
        data.put("pageInfo", Map.of("pageNum", pageNum, "pageSize", pageSize,
                "totalElements", (long) reportList.size()));
        data.put("pageList", pagedList);
        return Result.ok(data);
    }

    private String getStartTime(int contentType) {
        LocalDate now = LocalDate.now();
        return switch (contentType) {
            case 0 -> now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            case 1 -> now.minusDays(7).format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            case 2 -> now.withDayOfMonth(1).format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            default -> null;
        };
    }
}
