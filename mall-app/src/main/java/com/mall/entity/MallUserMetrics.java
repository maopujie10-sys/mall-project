package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_user_metrics")
public class MallUserMetrics {

    @TableId
    private String uuid;

    private String partyId;
    private Double moneyRechargeAcc;
    private Double storeMoneyRechargeAcc;
    private Double moneyWithdrawAcc;
    private Double accountBalance;
    private Double totleIncome;
    private Integer status;

    @Version
    private Integer version;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
