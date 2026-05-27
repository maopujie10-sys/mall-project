package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_cities")
public class MallCities {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String cityNameEn;
    private String cityNameTw;
    private String cityNameCn;
    private Long countryId;
    private Long stateId;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Integer flag;
}
