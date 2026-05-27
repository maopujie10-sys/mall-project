<%@ page language="java" pageEncoding="utf-8" isELIgnored="false"%>
<%@taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>

<style>
	.divider {
		margin: 4px 0;
		height: 1px;
		margin: 9px 0;
		overflow: hidden;
		background-color: #c8c1c1;
	}
	.sidebar-panel {
		background: none;
		margin: 33px 20px 0px 20px;
		border: none;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		padding: 15px 0px;
	}
</style>

<div class="sidebar clearfix">

	<ul class="sidebar-panel nav">

		<!-- dapp+交易所 菜单 ######################################################################################################## -->

		<%--        <c:choose>--%>
		<%--            <c:when test="${security.isRolesAccessible('ROLE_AGENT')}">--%>

		<%--                <li class="dropdown-parent">--%>
		<%--                    <a href="<%=basePath%>normal/adminUserAction!list.action">--%>
		<%--                        <span class="icon color6"><i class="fa fa-file-text-o"></i></span>--%>
		<%--                        <span class="sp-title">用户基础管理</span>--%>
		<%--                    </a>--%>
		<%--                </li>--%>

		<%--            </c:when>--%>
		<%--            <c:otherwise>--%>

		<li>
			<a href="<%=basePath%>normal/adminIndexAction!viewNew.action">
				<span class="icon color6"><i class="fa fa-home"></i></span>
				<span class="sp-title">综合查询</span>
			</a>
		</li>


		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                             || security.isResourceAccessible('OP_INVITE_CHECK')
                             || security.isResourceAccessible('OP_INVITE_OPERATE')}">



		</c:if>
		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                     || security.isResourceListAccessible('OP_EXCHANGE_USER_CHECK,OP_EXCHANGE_USER_OPERATE,OP_MARKET_CHECK,OP_MARKET_OPERATE,OP_EXCHANGE_WITHDRAW_CHECK,OP_EXCHANGE_WITHDRAW_OPERATE,OP_EXCHANGE_RECHARGE_CHECK,OP_EXCHANGE_RECHARGE_OPERATE')}">


			<li class="sidetitle">POS经理</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                             || security.isResourceAccessible('OP_CATEGORY_CHECK')
                             || security.isResourceAccessible('OP_CATEGORY_OPERATE')}">
			<li>
				<a href="<%=basePath%>mall/pos/list.action">
					<span class="icon color6"><i class="fa falist fa-laptop"></i></span>
					<span class="sp-title">POS下单</span>
				</a>
			</li>
		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                             || security.isResourceAccessible('OP_CATEGORY_CHECK')
                             || security.isResourceAccessible('OP_CATEGORY_OPERATE')}">
			<li>
				<a href="<%=basePath%>mall/pos/historylist.action">
					<span class="icon color6"><i class="fa falist fa-laptop"></i></span>
					<span class="sp-title">POS历史记录</span>
				</a>
			</li>
		</c:if>


		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                     || security.isResourceListAccessible('OP_EXCHANGE_USER_CHECK,OP_EXCHANGE_USER_OPERATE,OP_MARKET_CHECK,OP_MARKET_OPERATE,OP_EXCHANGE_WITHDRAW_CHECK,OP_EXCHANGE_WITHDRAW_OPERATE,OP_EXCHANGE_RECHARGE_CHECK,OP_EXCHANGE_RECHARGE_OPERATE')}">

			<%--            <li class="divider"></li>--%>

			<li class="sidetitle">财务</li>

		</c:if>




		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                     || security.isResourceAccessible('OP_EXCHANGE_WITHDRAW_CHECK')
                     || security.isResourceAccessible('OP_EXCHANGE_WITHDRAW_OPERATE')}">

			<li>
				<a href="<%=basePath%>normal/adminWithdrawAction!list.action">
					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>
					<span class="sp-title">提现订单</span>
					<span class="withdraw_order_untreated_cout badge label-danger" style="display: none">0</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                     || security.isResourceAccessible('OP_EXCHANGE_RECHARGE_CHECK')
                     || security.isResourceAccessible('OP_EXCHANGE_RECHARGE_OPERATE')}">

			<li>
				<a href="<%=basePath%>normal/adminRechargeBlockchainOrderAction!list.action">
					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>
					<span class="sp-title">充值订单</span>
					<span class="recharge_blockchain_order_untreated_cout badge label-danger" style="display: none">0</span>
				</a>
			</li>

		</c:if>


		<li class="sidetitle">业务</li>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN,ROLE_AGENT')
                             || security.isResourceAccessible('OP_USER_CHECK')
                             || security.isResourceAccessible('OP_USER_OPERATE')}">
			<li>
				<a href="<%=basePath%>normal/adminUserAction!list.action">
					<span class="icon color6"><i class="fa fa-file-text-o"></i></span>
					<span class="sp-title">用户管理</span>
				</a>
			</li>
		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                             || security.isResourceAccessible('OP_CATEGORY_CHECK')
                             || security.isResourceAccessible('OP_CATEGORY_OPERATE')}">
			<li>
				<a href="<%=basePath%>/mall/category/list.action?level=0">
					<span class="icon color6"><i class="fa falist fa-laptop"></i></span>
					<span class="sp-title">商品分类</span>
				</a>
			</li>
		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                             || security.isResourceAccessible('OP_CATEGORY_CHECK')
                             || security.isResourceAccessible('OP_CATEGORY_OPERATE')}">
			<li>
				<a href="<%=basePath%>mall/goods/list.action">
					<span class="icon color6"><i class="fa falist fa-laptop"></i></span>
					<span class="sp-title">商品库</span>
				</a>
			</li>
		</c:if>



		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
             || security.isResourceAccessible('OP_GOODATTRCATEGORY_CHECK')
             || security.isResourceAccessible('OP_GOODATTRCATEGORY_OPERATE')}">

			<li>
				<a href="<%=basePath%>/mall/goodAttrCategory/list.action">
					<span class="icon color6"><i class="fa falist fa-columns"></i></span>
					<span class="sp-title">属性管理</span>
				</a>
			</li>

		</c:if>



		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
             || security.isResourceAccessible('OP_GOODS_CHECK')
             || security.isResourceAccessible('OP_GOODS_OPERATE')}">

			<li>
				<a href="<%=basePath%>/mall/goods/sellerGoodsList.action">
					<span class="icon color6"><i class="fa falist fa-columns"></i></span>
					<span class="sp-title">店铺商品</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
             || security.isResourceAccessible('OP_LOANCOFIG_CHECK')}">

			<li>
				<a href="<%=basePath%>/mall/loan/config/toUpdate.action">
					<span class="icon color6"><i class="fa falist fa-columns"></i></span>
					<span class="sp-title">借贷配置</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
             || security.isResourceAccessible('OP_CREDIT_CHECK')
             || security.isResourceAccessible('OP_CREDIT_OPERATE')}">

			<li>
				<a href="<%=basePath%>/credit/history.action">
					<span class="icon color6"><i class="fa falist fa-columns"></i></span>
					<span class="sp-title">借贷记录</span>
					<span class="credit_untreated_cout badge label-danger" style="display: none">0</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                 || security.isResourceAccessible('OP_VIP_CHECK')}">

			<li>
				<a href="<%=basePath%>/brush/vip/list.action">
					<span class="icon color6"><i class="fa falist fa-outdent"></i></span>
					<span class="sp-title">卖家等级</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                 || security.isResourceAccessible('OP_MALL_ORDER_CHECK') || security.isResourceAccessible('OP_MALL_ORDER_OPERATE')}">

			<li>
				<a href="<%=basePath%>/mall/order/list.action">
					<span class="icon color6"><i class="fa-laptop"></i></span>
					<span class="sp-title">订单列表</span>
					<span class="goods_order_waitdeliver_count badge label-danger" style="display: none">0</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                 || security.isResourceAccessible('OP_MALL_RORDER_CHECK') || security.isResourceAccessible('OP_MALL_RORDER_OPERATE')}">

			<li>
				<a href="<%=basePath%>/mall/order/refundList.action">
					<span class="icon color6"><i class="fa-laptop"></i></span>
					<span class="sp-title">退货订单</span>
					<span class="goods_order_return_count badge label-danger" style="display: none">0</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                                 || security.isResourceAccessible('OP_USER_KYC_CHECK')
                                 || security.isResourceAccessible('OP_USER_KYC_OPERATE')}">

			<li>
				<a href="<%=basePath%>normal/adminKycAction!list.action">
					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>
					<span class="sp-title">店铺审核</span>
					<span class="kyc_untreated_cout badge label-danger" style="display: none">0</span>
				</a>
			</li>

		</c:if>
		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                                 || security.isResourceAccessible('OP_MALL_SELLER_CHECK')
                                 || security.isResourceAccessible('OP_MALL_SELLER_OPERATE')}">

			<li>
				<a href="<%=basePath%>/mall/seller/list.action">
					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>
					<span class="sp-title">店铺管理</span>
				</a>
			</li>

		</c:if>
		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                                 || security.isResourceAccessible('OP_COMBO_CHECK')
                                 || security.isResourceAccessible('OP_COMBO_OPERATE')}">

			<li>
				<a href="<%=basePath%>/mall/combo/list.action">
					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>
					<span class="sp-title">店铺直通车管理</span>
				</a>
			</li>

		</c:if>
		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                                 || security.isResourceAccessible('OP_COMBORECORD_CHECK')}">

			<li>
				<a href="<%=basePath%>/mall/combo/recordList.action">
					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>
					<span class="sp-title">直通车购买记录</span>
				</a>
			</li>

		</c:if>
<%--		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')--%>
<%--                                 || security.isResourceAccessible('OP_CHAT_CHECK')--%>
<%--                                 || security.isResourceAccessible('OP_CHAT_OPERATE')}">--%>

<%--			<li>--%>
<%--				<a href="<%=basePath%>/chat/chatsList.action">--%>
<%--					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>--%>
<%--					<span class="sp-title">虚拟买家对话</span>--%>
<%--					<span class="chat_untreated_cout badge label-danger" style="display: none">0</span>--%>
<%--				</a>--%>
<%--			</li>--%>
<%--		</c:if>--%>

<%--		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')--%>
<%--                                         || security.isResourceAccessible('OP_PLATFORMCHAT_CHECK')--%>
<%--                                         || security.isResourceAccessible('OP_PLATFORMCHAT_OPERATE')}">--%>
<%--			<li>--%>
<%--				<a href="<%=basePath%>/platform/chatsList.action">--%>
<%--					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>--%>
<%--					<span class="sp-title">系统客服对话</span>--%>
<%--				</a>--%>
<%--			</li>--%>


<%--		</c:if>--%>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                                         || security.isResourceAccessible('OP_CHAT_AUDIT_CHECK')
                                         || security.isResourceAccessible('OP_CHAT_AUDIT_OPERATE')}">
			<li>
				<a href="<%=basePath%>/chat/auditList.action">
					<span class="icon color6"><i class="fa falist fa-credit-card"></i></span>
					<span class="sp-title">买家对话审核</span>
					<span class="chat_mixed_unread_count badge label-danger" style="display: none">0</span>

				</a>
			</li>

		</c:if>




		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                     || security.isResourceListAccessible('OP_EXCHANGE_ALL_STATISTICS_CHECK,OP_EXCHANGE_AGENT_ALL_STATISTICS_CHECK,OP_EXCHANGE_USER_ALL_STATISTICS_CHECK')}">

			<li class="sidetitle">对账</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                            || security.isResourceAccessible('OP_EXCHANGE_ALL_STATISTICS_CHECK')}">

			<li>
				<a href="<%=basePath%>/brush/userMoney/list.action">
					<span class="icon color6"><i class="fa falist fa-pie-chart"></i></span>
					<span class="sp-title">用户存量</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                            || security.isResourceAccessible('OP_EXCHANGE_ALL_STATISTICS_CHECK')}">

			<li>
				<a href="<%=basePath%>normal/exchangeAdminAllStatisticsAction!list.action">
					<span class="icon color6"><i class="fa falist fa-pie-chart"></i></span>
					<span class="sp-title">运营数据</span>
				</a>
			</li>

		</c:if>

		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                            || security.isResourceAccessible('OP_EXCHANGE_AGENT_ALL_STATISTICS_CHECK')}">

			<li>
				<a href="<%=basePath%>normal/exchangeAdminAgentAllStatisticsAction!list.action">
					<span class="icon color6"><i class="fa falist fa-sitemap"></i></span>
					<span class="sp-title">代理商充提报表</span>
				</a>
			</li>

		</c:if>
		<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
                            || security.isResourceAccessible('OP_EXCHANGE_USER_ALL_STATISTICS_CHECK')}">

			<li>
				<a href="<%=basePath%>normal/adminUserAllStatisticsAction!exchangeList.action">
					<span class="icon color6"><i class="fa falist fa-align-left"></i></span>
					<span class="sp-title">用户报表</span>
				</a>
			</li>

		</c:if>


	</ul>

</div>