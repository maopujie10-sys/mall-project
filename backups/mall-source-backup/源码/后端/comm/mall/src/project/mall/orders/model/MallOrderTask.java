package project.mall.orders.model;

import kernel.bo.EntityObject;
import lombok.Data;

import java.util.Date;

@Data
public class MallOrderTask extends EntityObject {
    private static final long serialVersionUID = -6658359979884278L;
    private String orderOn;
    private Integer orderType;
    private String goodId;
    private String goodSku;
    private Integer goodCount;
    private String shopId;
    private Integer status;
    private Date taskTime;
    private Date createTime;
    private String addressId;
    private String partyId;
}
