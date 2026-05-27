package com.mall.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("mall_category")
public class Category {
    /** UUID主键，与现有数据库一致 */
    @TableId
    private String uuid;
    /** 排序 */
    private Integer sort;
    /** 图标 */
    private String iconImg;
    /** 记录时间（毫秒时间戳） */
    private Long recTime;
    /** 创建时间 */
    private java.time.LocalDateTime createTime;
    /** 状态 */
    private Integer status;
    /** 排序权重（MySQL8保留字，需转义） */
    @TableField("`rank`")
    private Integer rank;
    /** 层级（MySQL8保留字，需转义） */
    @TableField("`level`")
    private Integer level;
    /** 父级ID */
    private String parentId;
    /** 类型 */
    private Integer type;
    /** 分类名称 */
    private String name;
}
