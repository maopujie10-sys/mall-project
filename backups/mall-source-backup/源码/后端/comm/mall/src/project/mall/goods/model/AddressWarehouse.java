package project.mall.goods.model;

import kernel.bo.EntityObject;
import lombok.Data;

import java.util.Date;

@Data
public class AddressWarehouse extends EntityObject {
    private static final long serialVersionUID = 4050507877516757814L;

    private Integer id;
    private Integer zipcode;
    private String username;
    private String email;
    private String country;
    private String province;
    private String homeaddress;
    private String mobile;
    private String city;
    private Date create_time;
}
