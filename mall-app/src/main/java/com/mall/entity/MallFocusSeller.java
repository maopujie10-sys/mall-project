package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_focus_seller")
public class MallFocusSeller {

    @TableId
    private String uuid;

    private String partyId;
    private String sellerId;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
