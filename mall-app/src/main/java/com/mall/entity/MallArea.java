package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_area")
public class MallArea {
    @TableId
    private String uuid;
    private String areaName;
    private Integer areaType;
    private String parentUuid;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private String updateBy;
    private Integer status;
}
