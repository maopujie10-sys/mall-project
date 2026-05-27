package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_client_seller")
public class MallClientSeller {
    @TableId
    private String uuid;
    private String title;
    private Integer status;
    private String latestVersion;
    private String downloadlink;
    private String content;
}
