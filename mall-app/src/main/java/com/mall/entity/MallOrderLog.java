package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_order_log")
public class MallOrderLog {
    @TableId
    private String uuid;
    private String category;
    private String log;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private String partyId;
    private String username;
    private String orderId;
    private Integer state;
}
