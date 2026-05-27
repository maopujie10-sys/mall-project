package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.MallOrder;
import org.apache.ibatis.annotations.Mapper;

import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Mapper
public interface MallOrderMapper extends BaseMapper<MallOrder> {

    @Select("SELECT COUNT(*) FROM mall_order WHERE DATE(CREATE_TIME) = CURDATE()")
    Long countTodayOrders();

    @Select("SELECT IFNULL(SUM(PAY_AMOUNT), 0) FROM mall_order WHERE DATE(CREATE_TIME) = CURDATE() AND ORDER_STATUS IN (2, 3, 6)")
    BigDecimal sumTodayAmount();

    @Select("SELECT COUNT(*) FROM mall_order")
    Long countAll();

    @Select("SELECT order_status as status, COUNT(*) as count FROM mall_order GROUP BY order_status ORDER BY order_status")
    List<Map<String, Object>> countByStatus();

    @Select("SELECT DATE(create_time) as date, COUNT(*) as orders, IFNULL(SUM(pay_amount), 0) as amount FROM mall_order WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL #{days} DAY) AND order_status IN (2,3,6) GROUP BY DATE(create_time) ORDER BY date")
    List<Map<String, Object>> dailyStats(@Param("days") int days);
}
