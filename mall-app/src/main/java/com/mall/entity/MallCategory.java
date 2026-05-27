package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_category")
public class MallCategory {
    @TableId
    private String uuid;
    private Integer sort;
    private String iconImg;
    private Long recTime;
    private java.time.LocalDateTime createTime;
    private Integer status;
    @TableField("`rank`")
    private Integer rank;
    @TableField("`level`")
    private Integer level;
    private String parentId;
    private Integer type;
    private String name;
}
