package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("mall_goods_virtual_view")
public class MallGoodsVirtualView {
    @TableId
    private String uuid;
    private String partyId;
    private String comboId;
    private String comboRid;
    private String sellGoodsId;
    private Integer virtualNum;
    private Long incrTime;
}
