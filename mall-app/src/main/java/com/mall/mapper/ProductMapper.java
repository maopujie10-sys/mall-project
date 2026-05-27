package com.mall.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.mall.entity.Product;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface ProductMapper extends BaseMapper<Product> {

    @Update("UPDATE mall_product SET virtual_sales = virtual_sales + #{amount} WHERE id = #{id}")
    void addVirtualSales(@Param("id") Long id, @Param("amount") Integer amount);

    @Update("UPDATE mall_product SET virtual_views = virtual_views + #{amount} WHERE id = #{id}")
    void addVirtualViews(@Param("id") Long id, @Param("amount") Integer amount);

    @Update("UPDATE mall_goods_sku SET sale = sale - #{quantity} WHERE id = #{skuId} AND sale >= #{quantity}")
    int deductStock(@Param("skuId") String skuId, @Param("quantity") Integer quantity);
}
