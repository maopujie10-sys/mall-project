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
@TableName("mall_product_image")
public class ProductImage {
    @TableId(type = IdType.AUTO)
    private Long id;
    /** 商品ID */
    private Long productId;
    /** SKU ID */
    private Long skuId;
    /** 图片URL */
    private String imageUrl;
    /** COS对象存储地址 */
    private String cosUrl;
    /** 图片类型：1主图 2详情图 3SKU图 */
    private Integer type;
    /** 排序 */
    private Integer sort;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    @TableLogic
    private Integer deleted;
}
