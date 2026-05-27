package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_kyc")
public class Kyc {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String realName;
    private String nationality;
    private String idCardNo;
    /** ID_CARD/PASSPORT/DRIVER_LICENSE */
    private String idCardType;
    private String frontImg;
    private String backImg;
    private String handImg;
    /** 0=待审核 1=通过 2=拒绝 */
    private Integer status;
    private String rejectReason;
    private Long auditAdminId;
    private LocalDateTime auditTime;
    private LocalDateTime submitTime;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
