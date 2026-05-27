package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_combo_user")
public class MallComboUser {
    @TableId
    private String uuid;
    private String comboId;
    private Integer promoteNum;
    private Long stopTime;
}
