package project.web.admin.dto;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;

@Data
public class PosSku implements Serializable {
    private String id;
    private BigDecimal price;

}
