package com.mall.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_usdt_address")
public class UsdtAddress {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String network;
    private String address;
    private String label;
    private Integer isActive;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
