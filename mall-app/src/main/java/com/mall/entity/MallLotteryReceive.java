package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("mall_lottery_receive")
public class MallLotteryReceive {
    @TableId
    private String id;
    private String activityId;
    private String lotteryName;
    private String partyId;
    private String partyName;
    private String prizeIds;
    private Integer prizeType;
    private BigDecimal prizeAmount;
    private String recommendName;
    private String sellerName;
    private String remark;
    private Integer state;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private LocalDateTime applyTime;
    private LocalDateTime issueTime;
    private String createUser;
    private Integer activityType;
}
