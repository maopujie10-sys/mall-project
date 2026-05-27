package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_shopping_cart")
public class MallShoppingCart {
    @TableId
    private String uuid;
    private String partyId;
    private String goodsId;
    private String skuId;
    private Integer quantity;
    private Double price;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Integer status;
}
