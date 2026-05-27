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
@TableName("mall_merchant_apply")
public class MerchantApply {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private String shopName;
    private String shopPhone;
    private String shopAddress;
    private String contact;
    private String remark;
    /** 0=待审核 1=通过 2=拒绝 */
    private Integer status;
    private String rejectReason;
    private Long auditAdminId;
    private LocalDateTime auditTime;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
