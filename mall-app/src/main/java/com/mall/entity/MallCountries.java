package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_countries")
public class MallCountries {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String countryNameEn;
    private String countryNameTw;
    private String countryNameCn;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Integer flag;
}
