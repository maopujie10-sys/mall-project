package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_comment")
public class MallComment {
    @TableId
    private String uuid;
    private String goodId;
    private String username;
    private String category;
    private String content;
    private String date;
}
