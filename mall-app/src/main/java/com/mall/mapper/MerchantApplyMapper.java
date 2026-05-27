package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.MerchantApply;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface MerchantApplyMapper extends BaseMapper<MerchantApply> {

    @Select("SELECT COUNT(*) FROM mall_merchant_apply WHERE status = 0")
    Long countPending();
}
