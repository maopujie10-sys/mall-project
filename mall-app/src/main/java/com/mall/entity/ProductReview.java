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
@TableName("mall_evaluation")
public class ProductReview {
    /** UUID主键，与现有数据库一致 */
    @TableId
    private String uuid;
    /** 用户名 */
    private String userName;
    /** 卖家商品ID */
    private String sellerGoodsId;
    /** 卖家ID */
    private String sellerId;
    /** 评价类型 */
    private Integer evaluationType;
    /** 评分 */
    private Integer rating;
    /** 创建时间 */
    private LocalDateTime createTime;
    /** 评价内容 */
    private String content;
    /** 订单ID */
    private String orderId;
    /** 图片1 */
    private String imgUrl1;
    /** 图片2 */
    private String imgUrl2;
    /** 图片3 */
    private String imgUrl3;
    /** 图片4 */
    private String imgUrl4;
    /** 图片5 */
    private String imgUrl5;
    /** 图片6 */
    private String imgUrl6;
    /** 图片7 */
    private String imgUrl7;
    /** 图片8 */
    private String imgUrl8;
    /** 图片9 */
    private String imgUrl9;
    /** 状态 */
    private Integer status;
    /** 参与方ID */
    private String partyId;
    /** 参与方名称 */
    private String partyName;
    /** 参与方头像 */
    private String partyAvatar;
    /** 模板 */
    private String template;
    /** 来源类型 */
    private Integer sourceType;
    /** 评价时间 */
    private LocalDateTime evaluationTime;
    /** 商品状态 */
    private Integer goodsStatus;
    /** SKU ID */
    private String skuId;
    /** 国家ID */
    private Integer countryId;
    /** 系统商品ID */
    private String systemGoodsId;
}
