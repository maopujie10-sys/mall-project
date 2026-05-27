package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_combo_goods")
public class MallComboGoods {
    @TableId
    private String uuid;
    private String sellGoodsId;
    private String partyId;
    private String comboId;
    private String comboRid;
    private Long beginTime;
    private Long stopTime;
    private LocalDateTime createTime;
}
