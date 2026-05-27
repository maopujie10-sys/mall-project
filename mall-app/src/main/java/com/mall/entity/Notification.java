package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_notification")
public class Notification {
    @TableId(type = IdType.AUTO)
    private Long id;
    /** 接收用户ID，0=全站公告 */
    private Long userId;
    private String title;
    private String content;
    /** ORDER/SYSTEM/PROMOTION */
    private String type;
    /** 关联ID（订单号等） */
    private String relatedId;
    private Integer isRead;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
