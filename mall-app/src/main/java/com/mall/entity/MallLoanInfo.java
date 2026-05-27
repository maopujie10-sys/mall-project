package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_loan_info")
public class MallLoanInfo {
    @TableId
    private String uuid;
    private String loanId;
    private String realName;
    private String idNumber;
    private String nationality;
    private String photoFront;
    private String photoRear;
    private String photoHand;
}
