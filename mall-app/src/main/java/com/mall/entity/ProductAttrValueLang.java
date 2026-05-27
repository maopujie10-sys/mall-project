package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_goods_attribute_value_lang")
public class ProductAttrValueLang {
    @TableId
    private String id;
    private String name;
    private String lang;
    private Integer type;
    @TableField("ATTR_VALUE_ID")
    private String attrValueId;
}
