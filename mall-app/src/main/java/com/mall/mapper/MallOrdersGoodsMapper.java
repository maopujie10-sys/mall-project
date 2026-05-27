package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.MallOrdersGoods;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import java.util.List;
import java.util.Map;

@Mapper
public interface MallOrdersGoodsMapper extends BaseMapper<MallOrdersGoods> {

    @Select("SELECT system_goods_id as goodsId, SUM(goods_num) as totalSold " +
            "FROM mall_orders_goods GROUP BY system_goods_id " +
            "ORDER BY totalSold DESC LIMIT #{limit}")
    List<Map<String, Object>> topProducts(@Param("limit") int limit);
}
