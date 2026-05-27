package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_loan_config")
public class MallLoanConfig {
    @TableId
    private String uuid;
    private Double amountMin;
    private Double amountMax;
    private Double rate;
    private Double defaultRate;
    private String lendableDays;
    private String allLendableDays;
}
