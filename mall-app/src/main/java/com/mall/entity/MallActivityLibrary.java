package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_activity_library")
public class MallActivityLibrary {
    @TableId
    private String id;
    private String templateId;
    private String type;
    private String titleCn;
    private String titleEn;
    private String tags;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private Integer allowJoinTimes;
    private Integer status;
    private Integer isShow;
    private String activityConfig;
    private String joinRule;
    private String awardRule;
    private String detailUrl;
    private String imageUrl;
    private Integer location;
    private String descriptionCn;
    private String descriptionEn;
    private String lastOperator;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Integer deleted;
}
