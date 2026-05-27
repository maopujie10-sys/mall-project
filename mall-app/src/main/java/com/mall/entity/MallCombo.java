package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("mall_combo")
public class MallCombo {
    @TableId
    private String uuid;
    private String iconImg;
    private Integer promoteNum;
    private BigDecimal amount;
    private Integer day;
    private LocalDateTime createTime;
    private Integer baseAccessNum;
    private Integer autoAccMin;
    private Integer autoAccMax;
    private Integer accInterval;
}
