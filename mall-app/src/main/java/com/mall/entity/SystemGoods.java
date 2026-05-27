package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_system_goods")
public class SystemGoods {
    @TableId
    private String uuid;
    private String systemPrice;
    private String categoryId;
    private String secondaryCategoryId;
    private String goodsName;
    private String goodsDesc;
    private String mainImage;
    private String detailImages;
    private Integer status;
    private Integer isHot;
    private Integer isNew;
    private Integer sort;
    private String brandName;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
