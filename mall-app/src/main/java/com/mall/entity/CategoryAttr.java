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
@TableName("mall_goods_attribute_category")
public class CategoryAttr {
    /** UUID主键，与现有数据库一致 */
    @TableId
    private String id;
    /** 属性名称 */
    private String name;
    /** 排序 */
    private Integer sort;
    /** 创建时间 */
    private LocalDateTime createTime;
}
