package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("mall_activity_prize")
public class MallActivityPrize {
    @TableId
    private String id;
    private String poolId;
    private String activityId;
    private String prizeNameCn;
    private String prizeNameEn;
    private Integer prizeType;
    private BigDecimal prizeAmount;
    private Integer maxQuantity;
    private Integer leftQuantity;
    private BigDecimal odds;
    private Integer status;
    private Integer defaultPrize;
    private String image;
    private String remark;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private String createBy;
    private Integer deleted;
}
