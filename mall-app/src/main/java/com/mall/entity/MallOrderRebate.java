package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_rebate")
public class MallOrderRebate {
    @TableId
    private String uuid;
    private String orderId;
    private String partyId;
    @TableField("ORDER_PARTY_ID")
    private String fromPartyId;
    @TableField("REBATE")
    private Double rebateAmount;
    @TableField(exist = false)
    private Double rebateRate;
    private Integer level;
    @TableField(exist = false)
    private Integer status;
    @TableField("CREATE_TIME")
    private String createTime;
    @TableField(exist = false)
    private LocalDateTime updateTime;
}
