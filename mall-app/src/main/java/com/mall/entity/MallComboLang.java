package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_combo_lang")
public class MallComboLang {
    @TableId
    private String uuid;
    private String name;
    private String lang;
    private String content;
    private String comboId;
    private Integer status;
}
