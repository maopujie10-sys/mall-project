package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.MallActivityUser;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface MallActivityUserMapper extends BaseMapper<MallActivityUser> {

    @Update("UPDATE mall_activity_user SET allow_join_times = allow_join_times + #{times} WHERE id = #{id}")
    int addAllowJoinTimes(@Param("id") String id, @Param("times") int times);

    @Update("UPDATE mall_activity_user SET join_times = join_times + #{times} WHERE id = #{id}")
    int addJoinTimes(@Param("id") String id, @Param("times") int times);
}
