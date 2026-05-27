package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_idcode")
public class Idcode {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String target;

    private String code;

    private String type;

    private LocalDateTime expireAt;

    private Integer used;

    private String ip;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
