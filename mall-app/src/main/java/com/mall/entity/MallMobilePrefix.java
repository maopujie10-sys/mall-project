package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_mobile_prefix")
public class MallMobilePrefix {
    @TableId
    private String uuid;
    private String country;
    private String mobilePrefix;
}
