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
@TableName("mall_goods_attribute_value")
public class ProductAttrValue {
    @TableId
    private String id;
    @TableField("GOOD_ATTRIBUTE_ID")
    private String goodAttributeId;
    private LocalDateTime createTime;
}
