package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.MallActivityPrize;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface MallActivityPrizeMapper extends BaseMapper<MallActivityPrize> {

    /** 带库存校验的奖品数量减1，防超发 */
    @Update("UPDATE mall_activity_prize SET left_quantity = left_quantity - 1 WHERE id = #{id} AND left_quantity > 0")
    int decrementLeftQuantity(@Param("id") String id);
}
