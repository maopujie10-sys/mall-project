package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_banner")
public class MallBanner {
    @TableId
    private String uuid;
    private String imgUrl;
    private Integer sort;
    private String type;
    private String link;
    private String remarks;
    private Integer imgType;
    private LocalDateTime createTime;
}
