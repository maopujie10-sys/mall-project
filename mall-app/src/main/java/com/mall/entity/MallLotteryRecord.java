package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("mall_lottery_record")
public class MallLotteryRecord {
    @TableId
    private String id;
    private String partyId;
    private String partyName;
    private String sellerName;
    private String recommendName;
    private String prizeName;
    private String activityId;
    private String lotteryName;
    private Integer prizeType;
    private String prizeId;
    private String prizeImage;
    private BigDecimal prizeAmount;
    private Integer receiveState;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private LocalDateTime lotteryTime;
    private LocalDateTime receiveTime;
}
