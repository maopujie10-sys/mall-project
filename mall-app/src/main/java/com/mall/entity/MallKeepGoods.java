package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_keep_goods")
public class MallKeepGoods {
    @TableId
    private String uuid;
    private String partyId;
    private String sellerGoodsId;
    private LocalDateTime createTime;
}
