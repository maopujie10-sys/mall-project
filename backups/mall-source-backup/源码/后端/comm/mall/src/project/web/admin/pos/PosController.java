package project.web.admin.pos;

import kernel.exception.BusinessException;
import kernel.util.StringUtils;
import kernel.web.PageActionSupport;
import kernel.web.ResultObject;
import lombok.extern.slf4j.Slf4j;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.hibernate.criterion.Restrictions;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.ModelAndView;
import project.mall.goods.AdminMallGoodsService;
import project.mall.goods.PosService;
import project.mall.goods.model.AddressWarehouse;
import project.mall.orders.model.MallAddress;
import project.mall.type.AdminCategoryService;
import project.party.model.Party;
import project.web.admin.chat.AdminChatController;
import project.web.admin.dto.PosCreateDto;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/mall/pos")
@Slf4j
public class PosController extends PageActionSupport {
    private Logger logger = LogManager.getLogger(PosController.class);


    @Resource
    protected PosService posService;



    @RequestMapping("/list.action")
    public ModelAndView list(HttpServletRequest request,@RequestParam Map<String, String> allParams) {
        this.pageSize = 20;
        String error = request.getParameter("error");
        String goodName = request.getParameter("goodName"); //商品名称
        String goodId = request.getParameter("goodId");  //商品ID
        String sellerId = request.getParameter("sellerId");  //店铺ID
        String sellerName = request.getParameter("sellerName");  //店铺名称

        ModelAndView model = new ModelAndView("pos_list");
        this.checkAndSetPageNo(request.getParameter("pageNo"));
        List<Party> guestUsers = null;
        try {
            this.checkAndSetPageNo(request.getParameter("pageNo"));
            this.page = this.posService.pagedQuerySellerGoods
                    (
                            this.pageNo,
                            this.pageSize,
                            goodId, goodName,
                            sellerName,
                            getLoginPartyId(),
                            sellerId
                    );

             guestUsers = this.posService.selectByRolename();


            //资料库
        } catch (BusinessException e) {
            model.addObject("error", error);
            return model;
        } catch (Throwable t) {
            logger.error(" error ", t);
            model.addObject("error", "[ERROR] " + t.getMessage());
        }
        model.addObject("page",this.page);
        model.addObject("goodName",goodName);
        model.addObject("guestUsers",guestUsers);
        model.addObject("goodId",goodId);
        model.addObject("sellerName",sellerName);
        model.addObject("sellerId",sellerId);
        model.addObject("message",message);
        model.addObject("pageNo",pageNo);
        model.addObject("error",error);
        return model;
    }


    @RequestMapping("/historylist.action")
    public ModelAndView historyList(HttpServletRequest request,@RequestParam Map<String, String> allParams) {
        this.pageSize = 20;
        String orderon = request.getParameter("orderon"); //商品名称
        this.checkAndSetPageNo(request.getParameter("pageNo"));

        ModelAndView model = new ModelAndView("pos_history");
        try {
            this.checkAndSetPageNo(request.getParameter("pageNo"));
            this.page = this.posService.pagedQueryHistoryList
                    (
                            this.pageNo,
                            this.pageSize,
                            orderon
                    );
            //资料库
        } catch (BusinessException e) {
            model.addObject("error", error);
            return model;
        } catch (Throwable t) {
            logger.error(" error ", t);
            model.addObject("error", "[ERROR] " + t.getMessage());
        }
        model.addObject("orderon",orderon);
        model.addObject("page",this.page);
        model.addObject("message",message);
        model.addObject("pageNo",pageNo);
        model.addObject("error",error);
        return model;
    }



    @RequestMapping("/create_task.action")
    public Object createtask(HttpServletRequest request, @RequestBody PosCreateDto posCreateDto) {
        return posService.createtask(request,posCreateDto);
    }


    @RequestMapping("/address.action")
    public Object address(HttpServletRequest request, @RequestParam("id") String id) {
        ResultObject resultObject = new ResultObject();
        resultObject.setMsg("error");
        List<MallAddress> address = this.posService.queryListAddress(id);;
        if (address != null && !address.isEmpty()) {
            resultObject.setCode("1");
            resultObject.setData(address);
            resultObject.setMsg("获取成功");
            return resultObject;
        }
        return resultObject;
    }

    @RequestMapping("/address_info.action")
    public Object addressInfo(HttpServletRequest request, @RequestParam("id") String id) {
        ResultObject resultObject = new ResultObject();
        resultObject.setMsg("error");
        MallAddress address = this.posService.queryAddress(id);;
        if (address != null) {
            resultObject.setCode("1");
            resultObject.setData(address);
            resultObject.setMsg("获取成功");
            return resultObject;
        }
        return resultObject;
    }

}
