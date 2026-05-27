package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_level")
public class MallLevel {

    @TableId
    private String uuid;

    private String level;
    private String title;
    private String condExpr;
    private Double profitRationMin;
    private Double profitRationMax;
    private String promoteViewDaily;
    private Integer awardBaseView;
    private Integer awardViewMin;
    private Integer awardViewMax;
    private Integer upgradeCash;
    private Integer hasExclusiveService;
    private Integer recommendAtFirstPage;
    private Integer deliveryDays;
    private String updateBy;
    private Double sellerDiscount;
    private Integer teamNum;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
