package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_complaint")
public class MallComplaint {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String type;
    private String reason;
    private String images;
    private Integer status;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
