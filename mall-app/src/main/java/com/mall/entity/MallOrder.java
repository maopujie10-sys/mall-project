package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("mall_order")
public class MallOrder {
    @TableId
    private String uuid;
    private String orderNo;
    private String partyId;
    private BigDecimal totalAmount;
    private BigDecimal payAmount;
    private BigDecimal discountAmount;
    private Integer orderStatus;
    private Integer payStatus;
    private Integer deliveryStatus;
    private String receiverName;
    private String receiverPhone;
    private String receiverAddress;
    private String logisticsNo;
    private String logisticsCompany;
    private String remark;
    private LocalDateTime payTime;
    private LocalDateTime deliveryTime;
    private LocalDateTime finishTime;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
