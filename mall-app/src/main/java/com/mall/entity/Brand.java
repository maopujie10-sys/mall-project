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
@TableName("mall_brand")
public class Brand {
    @TableId(type = IdType.AUTO)
    private Long id;
    /** 品牌名称 */
    private String name;
    /** 品牌Logo */
    private String logo;
    /** 品牌描述 */
    private String description;
    /** 品牌官网 */
    private String website;
    /** 排序 */
    private Integer sort;
    /** 状态：0禁用 1启用 */
    private Integer status;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    @TableLogic
    private Integer deleted;
}
