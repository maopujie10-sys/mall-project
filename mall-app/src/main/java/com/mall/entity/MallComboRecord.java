package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("mall_combo_record")
public class MallComboRecord {
    @TableId
    private String uuid;
    private String partyId;
    private String comboId;
    private Integer promoteNum;
    private BigDecimal amount;
    private Integer day;
    private String name;
    private LocalDateTime createTime;
    private Long beginTime;
    private Long stopTime;
    private Integer baseAccessNum;
    private Integer autoAccMin;
    private Integer autoAccMax;
    private Integer accInterval;
}
