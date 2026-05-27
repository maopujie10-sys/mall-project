package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_user_address")
public class MallUserAddress {
    @TableId
    private String uuid;
    private String partyId;
    private String receiverName;
    private String receiverPhone;
    private String countryId;
    private String stateId;
    private String cityId;
    private String addressDetail;
    private String zipCode;
    private Integer isDefault;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Integer status;
}
