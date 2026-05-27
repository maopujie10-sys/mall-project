package project.mall.goods;

import com.alibaba.fastjson.JSONArray;
import kernel.web.Page;
import project.mall.goods.model.AddressWarehouse;
import project.mall.goods.model.SellerGoods;
import project.mall.orders.model.MallAddress;
import project.mall.orders.model.MallOrdersPrize;
import project.party.model.Party;
import project.web.admin.dto.PosCreateDto;

import javax.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;

public interface PosService {
    Page pagedQuerySellerGoods(int pageNo, int pageSize, String goodId, String goodName, String sellerName, String loginPartyId,String sellerId);

    Object createtask(HttpServletRequest request, PosCreateDto posCreateDto);

    List<MallAddress> queryListAddress(String id);

    List<Party> selectByRolename();

    MallAddress queryAddress(String id);


    Map<String, String> submitOrder(String partyId, String orderInfo, String addressId);


    Page pagedQueryHistoryList(int pageNo, int pageSize, String orderon);
}
