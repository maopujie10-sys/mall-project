package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_kyc_high_level")
public class KycHighLevel {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String workPlace;
    private String homePlace;
    private String relativesRelation;
    private String relativesName;
    private String relativesPlace;
    private String relativesPhone;
    private String idimg1;
    private String idimg2;
    private String idimg3;
    /** 0=已申请 1=审核中 2=通过 3=未通过 */
    private Integer status;
    private String msg;
    private LocalDateTime applyTime;
    private LocalDateTime operationTime;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
