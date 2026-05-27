package com.mall.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("mall_evaluation")
public class MallEvaluation {
    @TableId
    private String uuid;
    private String userName;
    private String sellerGoodsId;
    private String sellerId;
    private Integer evaluationType;
    private Integer rating;
    private LocalDateTime createTime;
    private String content;
    private String orderId;
    @TableField("IMG_URL_1")
    private String imgUrl1;
    @TableField("IMG_URL_2")
    private String imgUrl2;
    @TableField("IMG_URL_3")
    private String imgUrl3;
    @TableField("IMG_URL_4")
    private String imgUrl4;
    @TableField("IMG_URL_5")
    private String imgUrl5;
    @TableField("IMG_URL_6")
    private String imgUrl6;
    @TableField("IMG_URL_7")
    private String imgUrl7;
    @TableField("IMG_URL_8")
    private String imgUrl8;
    @TableField("IMG_URL_9")
    private String imgUrl9;
    private Integer status;
    private String partyId;
    private String partyName;
    private String partyAvatar;
    private String template;
    private Integer sourceType;
    private LocalDateTime evaluationTime;
    private Integer goodsStatus;
    private String skuId;
    private Integer countryId;
    private String systemGoodsId;
}
