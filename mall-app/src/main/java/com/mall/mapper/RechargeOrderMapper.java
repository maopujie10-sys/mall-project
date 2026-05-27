package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.RechargeOrder;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import java.math.BigDecimal;

@Mapper
public interface RechargeOrderMapper extends BaseMapper<RechargeOrder> {

    @Select("SELECT COUNT(*) FROM mall_recharge_order WHERE status = 0")
    Long countPending();

    @Select("SELECT IFNULL(SUM(amount), 0) FROM mall_recharge_order WHERE DATE(create_time) = CURDATE() AND status = 1")
    BigDecimal sumTodayRecharge();
}
