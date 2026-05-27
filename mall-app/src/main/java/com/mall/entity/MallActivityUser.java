package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_activity_user")
public class MallActivityUser {
    @TableId
    private String id;
    private String activityId;
    private String activityType;
    private String userId;
    private String triggerType;
    private LocalDateTime validBeginTime;
    private LocalDateTime validEndTime;
    private Long firstTriggerTime;
    private Long lastTriggerTime;
    private Integer allowJoinTimes;
    private Integer joinTimes;
    private Integer status;
    private Integer userType;
    private Long userRegistTime;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Integer deleted;
}
