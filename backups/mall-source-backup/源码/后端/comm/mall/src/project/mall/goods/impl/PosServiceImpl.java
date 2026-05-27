package project.mall.goods.impl;

import cn.hutool.core.collection.CollectionUtil;
import cn.hutool.core.util.IdUtil;
import cn.hutool.core.util.StrUtil;
import com.alibaba.fastjson.JSONArray;
import kernel.util.Arith;
import kernel.util.StringUtils;
import kernel.web.Page;
import kernel.web.PagedQueryDao;
import kernel.web.ResultObject;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections.CollectionUtils;
import org.hibernate.Criteria;
import org.hibernate.criterion.DetachedCriteria;
import org.hibernate.criterion.Order;
import org.hibernate.criterion.Property;
import org.hibernate.criterion.Restrictions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.orm.hibernate5.support.HibernateDaoSupport;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import project.Constants;
import project.mall.goods.GoodsAttributeService;
import project.mall.goods.PosService;
import project.mall.goods.SellerGoodsService;
import project.mall.goods.dto.SkuDto;
import project.mall.goods.model.*;
import project.mall.log.OrderLogService;
import project.mall.log.model.OrderLog;
import project.mall.log.model.OrderStatusEnum;
import project.mall.notification.utils.notify.client.NotificationHelperClient;
import project.mall.orders.GoodsOrdersService;
import project.mall.orders.model.MallAddress;
import project.mall.orders.model.MallOrdersGoods;
import project.mall.orders.model.MallOrdersPrize;
import project.mall.seller.MallLevelService;
import project.mall.seller.model.MallLevel;
import project.mall.seller.model.Seller;
import project.mall.type.CategoryLangService;
import project.mall.utils.IdUtils;
import project.party.PartyService;
import project.party.model.Party;
import project.party.recom.UserRecomService;
import project.redis.RedisHandler;
import project.syspara.Syspara;
import project.syspara.SysparaService;
import project.web.admin.dto.PosCreateDto;
import project.web.admin.dto.PosSku;
import util.RegexUtil;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.math.BigDecimal;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.regex.Pattern;

@Slf4j
public class PosServiceImpl extends HibernateDaoSupport implements PosService {
    @Resource
    private GoodsOrdersService goodsOrdersService;

    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    private PagedQueryDao pagedQueryDao;

    protected RedisHandler redisHandler;

    protected GoodsAttributeService goodsAttributeService;

    private SellerGoodsService sellerGoodsService;

    private NotificationHelperClient notificationHelperClient;

    private PartyService partyService;

    public PagedQueryDao getPagedQueryDao() {
        return pagedQueryDao;
    }

    public void setPagedQueryDao(PagedQueryDao pagedQueryDao) {
        this.pagedQueryDao = pagedQueryDao;
    }

    public RedisHandler getRedisHandler() {
        return redisHandler;
    }

    public void setRedisHandler(RedisHandler redisHandler) {
        this.redisHandler = redisHandler;
    }

    public GoodsAttributeService getGoodsAttributeService() {
        return goodsAttributeService;
    }

    public void setGoodsAttributeService(GoodsAttributeService goodsAttributeService) {
        this.goodsAttributeService = goodsAttributeService;
    }

    public SellerGoodsService getSellerGoodsService() {
        return sellerGoodsService;
    }

    public void setSellerGoodsService(SellerGoodsService sellerGoodsService) {
        this.sellerGoodsService = sellerGoodsService;
    }

    public CategoryLangService getCategoryLangService() {
        return categoryLangService;
    }

    public void setCategoryLangService(CategoryLangService categoryLangService) {
        this.categoryLangService = categoryLangService;
    }

    public UserRecomService getUserRecomService() {
        return userRecomService;
    }

    public void setUserRecomService(UserRecomService userRecomService) {
        this.userRecomService = userRecomService;
    }

    public JdbcTemplate getJdbcTemplate() {
        return jdbcTemplate;
    }

    public PartyService getPartyService() {
        return partyService;
    }

    public void setPartyService(PartyService partyService) {
        this.partyService = partyService;
    }

    public void setJdbcTemplate(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public OrderLogService getOrderLogService() {
        return orderLogService;
    }

    public void setOrderLogService(OrderLogService orderLogService) {
        this.orderLogService = orderLogService;
    }

    private OrderLogService orderLogService;

    protected CategoryLangService categoryLangService;

    private UserRecomService userRecomService;

    public SysparaService getSysparaService() {
        return sysparaService;
    }

    public void setSysparaService(SysparaService sysparaService) {
        this.sysparaService = sysparaService;
    }

    private SysparaService sysparaService;

    private JdbcTemplate jdbcTemplate;


    private MallLevelService mallLevelService;

    public MallLevelService getMallLevelService() {
        return mallLevelService;
    }

    public void setMallLevelService(MallLevelService mallLevelService) {
        this.mallLevelService = mallLevelService;
    }


    @Override
    public Page pagedQuerySellerGoods(int pageNo, int pageSize, String goodId, String goodName, String sellerName, String loginPartyId,String sellerId) {
        Page page = new Page();
        StringBuffer queryString = new StringBuffer();
        queryString.append(" SELECT ");
        queryString.append(" g.UUID id, l.NAME name, g.CATEGORY_ID categoryId, g.SECONDARY_CATEGORY_ID secondaryCategoryId, s.NAME sellerName, g.SYSTEM_PRICE systemPrice, g.GOODS_ID goodsId , g.BUY_MIN buyMin, g.SELLER_ID sellerId, g.SELL_WELL_TIME sellWellTime, ");
        queryString.append(" party.USERCODE usercode, g.SOLD_NUM soldNum, g.SELLING_PRICE sellingPrice, g.SYSTEM_NEW_TIME systemNewTime, g.SYSTEM_REC_TIME systemRecTime, g.SELLER_ID sellerId, g.REC_TIME recTime, g.NEW_TIME newTime, g.IS_SHELF isShelf, p.IMG_URL_1 cover ");
        queryString.append(" FROM ");
        queryString.append(" T_MALL_SELLER_GOODS g FORCE INDEX (idx_create_time) ");
        queryString.append(" LEFT JOIN T_MALL_SYSTEM_GOODS_LANG l ON g.GOODS_ID = l.GOODS_ID ");
        queryString.append(" LEFT JOIN T_MALL_SELLER s ON g.SELLER_ID = s.UUID ");
        queryString.append(" LEFT JOIN T_MALL_SYSTEM_GOODS p ON g.GOODS_ID = p.UUID ");
        queryString.append(" LEFT JOIN PAT_PARTY party ON g.SELLER_ID = party.UUID ");
        queryString.append(" WHERE 1=1 and IFNULL(l.LANG, 'en') = 'en' and l.TYPE = 0 and g.IS_VALID = 1 and s.status = 1");
        Map<String, Object> parameters = new HashMap<String, Object>();

        if (!StringUtils.isNullOrEmpty(goodName)) {
            queryString.append(" AND l.NAME like:goodName ");
            parameters.put("goodName", "%" + goodName + "%");
        }
        if (!StringUtils.isNullOrEmpty(goodId)) {
            queryString.append(" AND g.GOODS_ID =:goodId ");
            parameters.put("goodId", goodId);
        }

        if (!StringUtils.isNullOrEmpty(sellerName)) {
            queryString.append(" AND s.NAME LIKE :sellerName ");
            parameters.put("sellerName", "%" + sellerName + "%");
        }

        if (!StringUtils.isNullOrEmpty(sellerId)) {
            queryString.append(" AND party.USERCODE =:sellerId ");
            parameters.put("sellerId", sellerId);
        }
        queryString.append(" ORDER BY g.CREATE_TIME DESC ");
        page = this.pagedQueryDao.pagedQuerySQL(pageNo, pageSize, queryString.toString(), parameters);

        return page;
    }

    @Override
    public Object createtask(HttpServletRequest request, PosCreateDto posCreateDto) {
        ResultObject resultObject = new ResultObject();
        resultObject.setMsg("success");
        List<Map<String, Object>> order = posCreateDto.getOrder(); //订单列表
        String ordermode = posCreateDto.getOrdermode(); //pos方式
        String partyId = posCreateDto.getPartyId();
        String addressId = posCreateDto.getAddressId();
        //参数校验
        if (StrUtil.isBlank(ordermode) || StrUtil.isBlank(partyId) || StrUtil.isBlank(addressId) || order == null || order.isEmpty()) {
            resultObject.setCode("-1");
            resultObject.setMsg("参数不完整");
            return resultObject;
        }
        for (Map<String, Object> stringObjectMap : order) {
            String orderId = stringObjectMap.get("id").toString(); //店铺商品ID
            String buyCount = stringObjectMap.get("count").toString(); //购买数量
            //查询该商品
            SellerGoods sellerGoods = sellerGoodsService.getSellerGoods(orderId);
            //随机SKU
            String goodsId = sellerGoods.getGoodsId();
            String sql = "SELECT ID FROM T_MALL_GOODS_SKU WHERE GOOD_ID = '"+goodsId+"' ORDER BY RAND() LIMIT 1";
            String skuID = this.jdbcTemplate.queryForObject(sql, String.class);
            String orderInfo = orderId + "," + skuID + "," + buyCount;

            String shopId = "";
            if (("1").equals(ordermode)){
                Map<String, String> resultMap = submitOrder(partyId, orderInfo, addressId);

                if (resultMap.get("code").equals("200")){
                    String SQL = "INSERT INTO `T_MALL_ORDER_TASK` ( `UUID`, `ORDER_ON`, `ORDER_TYPE`,  `GOOD_ID`, `GOOD_ID_SKU`, `GOOD_COUNT`, `SHOP_ID`, `STATUS`, `TASK_TIME`, `CREATE_TIME`,`ADDRESS_ID`,`PARTY_ID`)" +
                            "VALUES (?,?,?,?,?,?,?,1,?,NOW(),?,?)";
                    Date currentDate = new Date();
                    jdbcTemplate.update(SQL, IdUtil.simpleUUID(),resultMap.get("orderId"),ordermode,orderId,skuID,buyCount,sellerGoods.getSellerId(),currentDate,addressId,partyId);
                }
            }else{
                String datePicker = posCreateDto.getDatePicker(); //时间
                if (StrUtil.isBlank(datePicker)){
                    resultObject.setCode("-1");
                    resultObject.setMsg("请选择下单时间");
                    return resultObject;
                }
                String SQL = "INSERT INTO `T_MALL_ORDER_TASK` ( `UUID`, `ORDER_ON`, `ORDER_TYPE`,`GOOD_ID`, `GOOD_ID_SKU`, `GOOD_COUNT`, `SHOP_ID`, `STATUS`, `TASK_TIME`, `CREATE_TIME`,`ADDRESS_ID`,`PARTY_ID`)" +
                "VALUES (?,?,?,?,?,?,?,0,?, NOW(),?,?)";
                jdbcTemplate.update(SQL, IdUtil.simpleUUID(),"-",ordermode,orderId,skuID,buyCount,sellerGoods.getSellerId(),datePicker,addressId,partyId);
            }

        }

        return resultObject;
    }


    @Override
    public List<MallAddress> queryListAddress(String id) {
        DetachedCriteria criteria = DetachedCriteria.forClass(MallAddress.class);
        criteria.add(Restrictions.eq("partyId", id));
        List<MallAddress> list = (List<MallAddress>) this.getHibernateTemplate().findByCriteria(criteria);
        return list;
    }

    @Override
    public List<Party> selectByRolename() {
        DetachedCriteria criteria = DetachedCriteria.forClass(Party.class);
        criteria.add(Restrictions.eq("rolename", Constants.SECURITY_ROLE_GUEST));
        List<Party> list = (List<Party>) this.getHibernateTemplate().findByCriteria(criteria);
        return list;
    }

    @Override
    public MallAddress queryAddress(String id) {
        MallAddress address = this.getHibernateTemplate().get(MallAddress.class, id);
        return address;
    }

    @Override
    public Map<String, String> submitOrder(String partyId, String orderInfo, String addressId) {
        return goodsOrdersService.saveOrderSubmitForTask(partyId, orderInfo, addressId);
    }

    @Override
    public Page pagedQueryHistoryList(int pageNo, int pageSize, String orderon) {
        Page page = new Page();
        StringBuffer queryString = new StringBuffer();
        queryString.append("SELECT task.CREATE_TIME,task.ORDER_ON,task.ORDER_TYPE,task.GOOD_COUNT,task.GOOD_ID_SKU,task.STATUS,task.TASK_TIME,task.CREATE_TIME,sellergoods.GOODS_ID,lang.`NAME`,seller.NAME AS shopname");
        queryString.append(" FROM ");
        queryString.append(" T_MALL_ORDER_TASK AS task, ");
        queryString.append(" T_MALL_SELLER_GOODS AS sellergoods, ");
        queryString.append(" T_MALL_SYSTEM_GOODS_LANG  AS lang, ");
        queryString.append(" T_MALL_SELLER AS seller ");
        queryString.append(" WHERE ");
        queryString.append(" task.GOOD_ID = sellergoods.UUID and lang.LANG = 'cn' and sellergoods.GOODS_ID = lang.GOODS_ID AND sellergoods.SELLER_ID = seller.UUID ");

        Map<String, Object> parameters = new HashMap<String, Object>();

        if (!StringUtils.isNullOrEmpty(orderon)) {
            queryString.append(" AND task.ORDER_ON =:ORDER_ON ");
            parameters.put("ORDER_ON",orderon);
        }

        queryString.append(" ORDER BY task.CREATE_TIME DESC ");
        page = this.pagedQueryDao.pagedQuerySQL(pageNo, pageSize, queryString.toString(), parameters);
        return page;

    }


}
