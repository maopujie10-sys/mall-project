package project.web.admin.dto;

import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class PosCreateDto {
    private String ordermode;
    private String datePicker;
    private String addressId;
    private String partyId;
    private List<Map<String,Object>> order;
}
