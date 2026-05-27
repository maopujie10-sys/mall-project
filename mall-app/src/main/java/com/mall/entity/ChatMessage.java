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
@TableName("mall_chat_message")
public class ChatMessage {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String conversationId;
    private Long fromUserId;
    private Long toUserId;
    private String content;
    private String msgType;
    private Integer isRead;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
