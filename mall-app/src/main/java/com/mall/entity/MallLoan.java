package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_loan")
public class MallLoan {
    @TableId
    private String uuid;
    private String partyId;
    private String refId;
    private Integer accType;
    private String userName;
    private Integer status;
    private Integer limitDay;
    private Double principal;
    private Double rate;
    private Double interest;
    private Double priAndInt;
    private Double actual;
    private String reject;
    private LocalDateTime submitTime;
    private LocalDateTime auditTime;
    private LocalDateTime lastPayTime;
    private Integer loanMethod;
}
