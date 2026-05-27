package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_goods_sku")
public class ProductSku {
    /** UUID主键，与现有数据库一致 */
    @TableId
    private String id;
    /** 商品ID */
    private String goodId;
    /** SKU价格 */
    private BigDecimal price;
    /** 图片 */
    private String pic;
    /** 封面图 */
    private String coverImg;
    /** 图标 */
    private String iconImg;
    /** 销量/库存数 */
    private Integer sale;
    /** 促销价 */
    private BigDecimal promotionPrice;
    /** 规格数据JSON */
    private String spData;
    /** 逻辑删除 */
    @TableLogic
    private Integer deleted;
}
