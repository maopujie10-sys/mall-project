package com.mall.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_domain_rotation")
public class DomainRotation {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String domain;
    private String role;
    private String status;
    private Long clicks;
    private String blockedReason;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
