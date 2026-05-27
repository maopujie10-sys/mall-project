package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_activity_user_points")
public class MallActivityUserPoints {
    @TableId
    private String id;
    private String partyId;
    private String activityType;
    private String activityId;
    private Integer points;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Integer deleted;
}
