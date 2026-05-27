package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_orders_prize")
public class MallOrdersPrize {
    @TableId
    private String uuid;
    private String partyId;
    private String userCode;
    private String sellerId;
    private Double prizeOriginal;
    private String sellerName;
    private Integer goodsCount;
    private Double prizeReal;
    private Double systemPrice;
    private Integer status;
    private Integer returnStatus;
    private Integer orderStatus;
    private Double fees;
    private Double tax;
    private Double profit;
    private LocalDateTime payTime;
    private Integer payStatus;
    private Long upTime;
    private LocalDateTime createTime;
    private String phone;
    private String email;
    private String contacts;
    private String postcode;
    private String country;
    private String province;
    private String city;
    private String address;
    private Integer profitStatus;
    private Integer purchStatus;
    private Integer purchTimeOutStatus;
    private LocalDateTime purchTimeOutTime;
    private LocalDateTime purchTime;
    private LocalDateTime refundTime;
    private LocalDateTime refundDealTime;
    private String refundRemark;
    private String returnReason;
    private String returnDetail;
    private Integer hasComment;
    private Integer countryId;
    private Integer provinceId;
    private Integer cityId;
    private Integer flag;
    private Double sellerDiscount;
    private Integer manualReceiptStatus;
    private Double pushAmount;
    private Integer manualShipStatus;
    private Integer isDelete;
    private Integer statusBeforeLastRefund;
}
