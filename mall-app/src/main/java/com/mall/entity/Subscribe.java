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
@TableName("mall_subscribe")
public class Subscribe {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    /** ORDER/SYSTEM/PROMOTION/CHAT */
    private String type;
    /** 订阅目标 */
    private String target;
    /** APP/EMAIL/WHATSAPP/TELEGRAM */
    private String channel;
    /** 0=关闭 1=启用 */
    private Integer enabled;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
