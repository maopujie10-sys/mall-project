package project.blockchain.internal;

import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import cn.hutool.core.util.IdUtil;
import kernel.web.ResultObject;
import org.hibernate.criterion.DetachedCriteria;
import org.hibernate.criterion.Property;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.orm.hibernate5.support.HibernateDaoSupport;

import kernel.util.StringUtils;
import kernel.web.Page;
import kernel.web.PagedQueryDao;
import project.blockchain.AdminChannelBlockchainService;
import project.blockchain.ChannelBlockchain;
import project.blockchain.PartyBlockchain;

import javax.servlet.http.HttpServletRequest;

public class AdminChannelBlockchainServiceImpl extends HibernateDaoSupport implements AdminChannelBlockchainService {
	private PagedQueryDao pagedQueryDao;

	private JdbcTemplate jdbcTemplate;

	public PagedQueryDao getPagedQueryDao() {
		return pagedQueryDao;
	}

	public JdbcTemplate getJdbcTemplate() {
		return jdbcTemplate;
	}

	public void setJdbcTemplate(JdbcTemplate jdbcTemplate) {
		this.jdbcTemplate = jdbcTemplate;
	}

	public Page pagedQuery(int pageNo, int pageSize, String name_para, String coin_para) {
		StringBuffer queryString = new StringBuffer(
				" SELECT channelblockchain.UUID id,channelblockchain.BLOCKCHAIN_NAME blockchain_name,"
						+ "channelblockchain.IMG img ,channelblockchain.COIN coin,  "
						+ " channelblockchain.ADDRESS address ");

		queryString.append(" FROM T_CHANNEL_BLOCKCHAIN channelblockchain WHERE 1 = 1 ");
		Map<String, Object> parameters = new HashMap<>();
		if (!StringUtils.isNullOrEmpty(name_para)) {
			queryString.append(" and  channelblockchain.BLOCKCHAIN_NAME like :name ");
			parameters.put("name", "%" + name_para + "%");
		}
		if (!StringUtils.isNullOrEmpty(coin_para)) {
			queryString.append(" and  channelblockchain.COIN like :coin ");
			parameters.put("coin", "%" + coin_para + "%");
		}
		Page page = this.pagedQueryDao.pagedQuerySQL(pageNo, pageSize, queryString.toString(), parameters);
		return page;
	}

	@Override
	public Page pagedPersonQuery(int pageNo, int pageSize, String userName, String roleName, String chainName, String coinSymbol, String address) {
		StringBuffer queryString = new StringBuffer(
				" SELECT USER_NAME,party.ROLENAME,party.USERCODE,CHAIN_NAME,COIN_SYMBOL,ADDRESS,AUTO,chain.CREATE_TIME FROM T_PARTY_BLOCKCHAIN chain " +
						"LEFT JOIN PAT_PARTY party ON party.USERNAME = chain.USER_NAME WHERE 1 = 1 ");
		Map<String, Object> parameters = new HashMap<>();
		if (!StringUtils.isNullOrEmpty(address)) {
			queryString.append(" AND chain.ADDRESS =:address ");
			parameters.put("address", address);
		}
		if (!StringUtils.isNullOrEmpty(userName)) {
			queryString.append(" AND (chain.USER_NAME LIKE :userName OR party.USERCODE LIKE :userName)  ");
			parameters.put("userName", "%" + userName + "%");
		}
		if (!StringUtils.isNullOrEmpty(roleName)) {
			queryString.append(" AND party.ROLENAME = :roleName ");
			parameters.put("roleName", roleName);
		}
		Page page = this.pagedQueryDao.pagedQuerySQL(pageNo, pageSize, queryString.toString(), parameters);
		return page;
	}

	@Override
	public ResultObject toAdd(HttpServletRequest request) {
		ResultObject resultObject = new ResultObject();
		String coin = request.getParameter("coin");
		String chain_name = request.getParameter("chain_name");
		String address = request.getParameter("address");
		resultObject.setCode("200");
		resultObject.setMsg("新增成功");
		if (StringUtils.isNullOrEmpty(address)) {
			resultObject.setCode("-1");
			resultObject.setMsg("收款地址不可为空");
			return resultObject;
		}

		if (StringUtils.isNullOrEmpty(coin)) {
			resultObject.setCode("-1");
			resultObject.setMsg("货币不可为空");
			return resultObject;
		}

		if (StringUtils.isNullOrEmpty(chain_name)) {
			resultObject.setCode("-1");
			resultObject.setMsg("区块网络不可为空");
			return resultObject;
		}

		String SQL = "INSERT INTO `T_CHANNEL_BLOCKCHAIN` (`UUID`, `BLOCKCHAIN_NAME`, `IMG`, `ADDRESS`, `COIN`, `AUTO`)" +
				"VALUES (?,?,?,?,?,?)";
		int update = jdbcTemplate.update(SQL, IdUtil.simpleUUID(), chain_name, "OBJK", address, coin, "N");
		if (update == 0){
			resultObject.setCode("-1");
			resultObject.setMsg("新增失败请重试");
			return resultObject;
		}

		return resultObject;
	}

	@Override
	public ResultObject toUpdate(HttpServletRequest request) {
		ResultObject resultObject=new ResultObject();
		String id = request.getParameter("id");
		String coin = request.getParameter("coin");
		String chain_name = request.getParameter("chain_name");
		String address = request.getParameter("address");
		resultObject.setCode("200");
		resultObject.setMsg("修改成功");
		if (StringUtils.isNullOrEmpty(id)) {
			resultObject.setCode("-1");
			resultObject.setMsg("ID不可为空");
			return resultObject;
		}

		if (StringUtils.isNullOrEmpty(address)) {
			resultObject.setCode("-1");
			resultObject.setMsg("收款地址不可为空");
			return resultObject;
		}

		if (StringUtils.isNullOrEmpty(coin)) {
			resultObject.setCode("-1");
			resultObject.setMsg("货币不可为空");
			return resultObject;
		}

		if (StringUtils.isNullOrEmpty(coin)) {
			resultObject.setCode("-1");
			resultObject.setMsg("区块网络不可为空");
			return resultObject;
		}



		String SQL = "UPDATE T_CHANNEL_BLOCKCHAIN SET BLOCKCHAIN_NAME= ?,ADDRESS = ?,COIN = ? WHERE UUID = ?";
		int update = jdbcTemplate.update(SQL,chain_name,address,coin,id);
		if (update == 0){
			resultObject.setCode("-1");
			resultObject.setMsg("修改失败请重试");
			return resultObject;
		}

		return resultObject;
	}

	@Override
	public ResultObject toDelete(HttpServletRequest request) {
		ResultObject resultObject=new ResultObject();
		String id = request.getParameter("id");
		resultObject.setCode("200");
		resultObject.setMsg("删除成功");
		if (StringUtils.isNullOrEmpty(id)) {
			resultObject.setCode("-1");
			resultObject.setMsg("ID不可为空");
			return resultObject;
		}

		String SQL = "DELETE FROM T_CHANNEL_BLOCKCHAIN  WHERE UUID = ?";
		int update = jdbcTemplate.update(SQL,id);
		if (update == 0){
			resultObject.setCode("-1");
			resultObject.setMsg("删除失败请重试");
			return resultObject;
		}
		return resultObject;
	}

	@Override
	public ResultObject selectById(HttpServletRequest request) {
		ResultObject resultObject = new ResultObject();
		ChannelBlockchain PartyBlockchain = getHibernateTemplate().get(ChannelBlockchain.class, request.getParameter("id"));
		resultObject.setCode("200");
		resultObject.setMsg("获取成功");
		resultObject.setData(PartyBlockchain);
		return resultObject;
	}

	public void setPagedQueryDao(PagedQueryDao pagedQueryDao) {
		this.pagedQueryDao = pagedQueryDao;
	}
}
