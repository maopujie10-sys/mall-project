package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_credit")
public class MallCredit {
    @TableId
    private String uuid;
    private String partyId;
    private Integer status;
    private String realName;
    private String identification;
    private Integer countryId;
    private String imgCertificateFace;
    private String imgCertificateBack;
    private String imgCertificateHand;
    private Integer creditPeriod;
    private Double applyAmount;
    private Double creditRate;
    private Double defaultRate;
    private Double totalInterest;
    private Double totalRepayment;
    private Double actualRepayment;
    private String rejectReason;
    private LocalDateTime customerSubmitTime;
    private LocalDateTime systemAuditTime;
    private LocalDateTime finalRepayTime;
    private LocalDateTime expireTime;
}
