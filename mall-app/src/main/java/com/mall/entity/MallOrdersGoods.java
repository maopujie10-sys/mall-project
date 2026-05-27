package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;

@Data
@TableName("mall_orders_goods")
public class MallOrdersGoods {
    @TableId
    private String uuid;
    private String orderId;
    private String goodsId;
    private Integer goodsNum;
    private BigDecimal goodsPrize;
    private BigDecimal goodsReal;
    private BigDecimal systemPrice;
    private BigDecimal fees;
    private BigDecimal tax;
    private Integer goodsSort;
    private String systemGoodsId;
    private String skuId;
}
