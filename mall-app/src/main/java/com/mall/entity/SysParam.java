package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_sys_param")
public class SysParam {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String paramKey;

    private String paramValue;

    private String paramType;

    private String description;

    private Integer editable;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
