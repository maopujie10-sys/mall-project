package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("mall_seller")
public class MallSeller {
    @TableId
    private String id;
    private String name;
    private String keyWords;
    private String avatar;
    private String contact;
    private String shopPhone;
    private String shopRemark;
    private String shopAddress;
    private String banner1;
    private String banner2;
    private Integer status;
    private String partyId;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;

    @TableField("MALL_LEVEL")
    private String mallLevel;

    @TableField("INVITE_NUM")
    private Integer inviteNum;

    @TableField("TEAM_NUM")
    private Integer teamNum;

    @TableField("CHILD_NUM")
    private Integer childNum;

    @TableField("CREDIT_SCORE")
    private Integer creditScore;

    @TableField("INVITE_AMOUNT_REWARD")
    private BigDecimal inviteAmountReward;

    @TableField("RECHARGE_BONUS")
    private BigDecimal rechargeBonus;

    @TableField("RECHARGE_BONUS_STATUS")
    private Integer rechargeBonusStatus;

    @TableField("BLACK")
    private Integer black;

    @TableField("REALS")
    private Integer reals;

    @TableField("FAKE")
    private Integer fake;

    @TableField("FAKE_SOLD_NUM")
    private Integer fakeSoldNum;
}
