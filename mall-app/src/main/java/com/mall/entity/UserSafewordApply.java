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
@TableName("mall_user_safeword_apply")
public class UserSafewordApply {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    /** 证件正面照 */
    private String idcardPathFront;
    /** 证件背面照 */
    private String idcardPathBack;
    /** 手持证件照 */
    private String idcardPathHold;
    /** 新的资金密码(BCrypt) */
    private String safeword;
    /** 1=审核中 2=通过 3=拒绝 */
    private Integer status;
    /** 审核消息/拒绝原因 */
    private String msg;
    /** 操作类型: 0=重置资金密码 1=解绑谷歌 2=解绑手机 3=解绑邮箱 */
    private Integer operate;
    /** 备注 */
    private String remark;
    /** 审核人ID */
    private Long auditAdminId;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    private LocalDateTime applyTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
