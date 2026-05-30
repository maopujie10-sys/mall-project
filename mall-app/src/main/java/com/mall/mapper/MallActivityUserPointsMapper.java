package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.MallActivityUserPoints;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface MallActivityUserPointsMapper extends BaseMapper<MallActivityUserPoints> {

    @Update("UPDATE mall_activity_user_points SET points = points - #{points} WHERE id = #{id}")
    int deductPoints(@Param("id") String id, @Param("points") int points);

    @Update("UPDATE mall_activity_user_points SET points = points + #{points} WHERE id = #{id}")
    int addPoints(@Param("id") String id, @Param("points") int points);
}
