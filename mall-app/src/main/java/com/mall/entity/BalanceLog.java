package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_balance_log")
public class BalanceLog {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    /** 金额（正=收入 负=支出） */
    private BigDecimal amount;
    /** RECHARGE/WITHDRAW/ORDER/REFUND/ADMIN_ADJUST */
    private String type;
    private String remark;
    private Long relatedId;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
