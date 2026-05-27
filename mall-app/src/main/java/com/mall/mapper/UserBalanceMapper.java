package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.UserBalance;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;
import java.math.BigDecimal;

@Mapper
public interface UserBalanceMapper extends BaseMapper<UserBalance> {

    @Update("UPDATE mall_user_balance SET balance = balance + #{amount} WHERE user_id = #{userId}")
    void addBalance(@Param("userId") Long userId, @Param("amount") BigDecimal amount);

    @Update("UPDATE mall_user_balance SET balance = balance - #{amount}, version = version + 1 WHERE user_id = #{userId} AND balance >= #{amount} AND version = #{version}")
    int deductBalance(@Param("userId") Long userId, @Param("amount") BigDecimal amount, @Param("version") Integer version);

    @Update("UPDATE mall_user_balance SET balance = balance - #{amount}, frozen = frozen + #{amount}, version = version + 1 WHERE user_id = #{userId} AND balance >= #{amount} AND version = #{version}")
    int freezeBalance(@Param("userId") Long userId, @Param("amount") BigDecimal amount, @Param("version") Integer version);

    @Update("UPDATE mall_user_balance SET frozen = frozen - #{amount} WHERE user_id = #{userId}")
    int deductFrozen(@Param("userId") Long userId, @Param("amount") BigDecimal amount);

    @Update("UPDATE mall_user_balance SET balance = balance + #{amount}, frozen = frozen - #{amount} WHERE user_id = #{userId}")
    int unfreezeBalance(@Param("userId") Long userId, @Param("amount") BigDecimal amount);
}
