package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_states")
public class MallStates {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String stateNameEn;
    private String stateNameTw;
    private String stateNameCn;
    private Long countryId;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Integer flag;
}
