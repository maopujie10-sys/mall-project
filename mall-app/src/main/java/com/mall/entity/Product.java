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
@TableName("mall_product")
public class Product {
    @TableId(type = IdType.AUTO)
    private Long id;
    /** 分类ID */
    private Long categoryId;
    /** 品牌ID */
    private Long brandId;
    /** 商家ID */
    private Long merchantId;
    /** 商品名称 */
    private String name;
    /** 副标题 */
    private String subtitle;
    /** 主图 */
    private String mainImage;
    /** 详情图（JSON数组） */
    private String detailImages;
    /** 销售价 */
    private BigDecimal price;
    /** 原价 */
    private BigDecimal originalPrice;
    /** 成本价 */
    private BigDecimal costPrice;
    /** 总库存 */
    private Integer totalStock;
    /** 销量 */
    private Integer sales;
    /** 虚拟销量 */
    private Integer virtualSales;
    /** 虚拟浏览量 */
    private Integer virtualViews;
    /** 状态：0下架 1上架 */
    private Integer status;
    /** 是否热门 */
    private Integer isHot;
    /** 是否新品 */
    private Integer isNew;
    /** 排序 */
    private Integer sort;
    /** 商品描述 */
    private String description;
    /** 商品单位 */
    private String unit;
    /** 是否为B2B批发商品 */
    private Integer isWholesale;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    @TableLogic
    private Integer deleted;
}
