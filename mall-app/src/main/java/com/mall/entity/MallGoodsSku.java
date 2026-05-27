package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;

@Data
@TableName("mall_goods_sku")
public class MallGoodsSku {
    @TableId
    private String id;
    private String goodId;
    private BigDecimal price;
    private String pic;
    private String coverImg;
    private String iconImg;
    private Integer sale;
    private BigDecimal promotionPrice;
    private String spData;
    private Integer deleted;
}
