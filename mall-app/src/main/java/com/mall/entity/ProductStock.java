package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_product_stock")
public class ProductStock {
    @TableId(type = IdType.AUTO)
    private Long id;
    /** 商品ID */
    private Long productId;
    /** SKU ID */
    private Long skuId;
    /** 总库存 */
    private Integer totalStock;
    /** 锁定库存（下单未支付） */
    private Integer lockStock;
    /** 可用库存 */
    private Integer availableStock;
    /** 安全库存预警值 */
    private Integer alertStock;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    @TableLogic
    private Integer deleted;
}
