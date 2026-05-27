package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("mall_seller_goods")
public class SellerGoods {
    @TableId
    private String uuid;
    private String sellerId;
    private String systemGoodsId;
    private BigDecimal price;
    private Integer stock;
    private String goodsName;
    private String coverImg;
    private String iconImg;
    private String goodsDesc;
    private Integer status;
    private Integer verifyStatus;
    private Integer saleCount;
    private Integer viewCount;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
