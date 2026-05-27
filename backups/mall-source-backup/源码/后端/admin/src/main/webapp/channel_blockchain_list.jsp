<%@ page language="java" pageEncoding="utf-8" isELIgnored="false"%>
<%@taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>
<jsp:useBean id="security" class="security.web.BaseSecurityAction" scope="page" />

<%@ include file="include/pagetop.jsp"%>

<!DOCTYPE html>
<html>

<head>
<%@ include file="include/head.jsp"%>
</head>

<body>

	<%@ include file="include/loading.jsp"%>
	<%-- 	<%@ include file="include/top.jsp"%> --%>
	<%-- 	<%@ include file="include/menu_left.jsp"%> --%>

	<!-- //////////////////////////////////////////////////////////////////////////// -->
	<!-- START CONTENT -->
	<div class="ifr-dody">

		<!-- //////////////////////////////////////////////////////////////////////////// -->
		<!-- START CONTAINER -->
		<div class="ifr-con">
			<h3>区块链充值地址维护</h3>

			<!-- //////////////////////////////////////////////////////////////////////////// -->
			<!-- START queryForm -->
			<%@ include file="include/alert.jsp"%>

			<div class="row">
				<div class="col-md-12">
				
					<!-- Start Panel -->
					<div class="panel panel-default">
						<div class="panel-title">查询结果</div>
						
						<!-- <sec:authorize ifAnyGranted="ROLE_ROOT"> -->
						<c:if test="${security.isRolesAccessible('ROLE_ROOT')}">

							<a onclick="add()" class="btn btn-light" style="margin-bottom: 10px">
								<i class="fa fa-pencil"></i>新增</a>

						<!-- </sec:authorize> -->
						</c:if>
						
						<div class="panel-body">

							<table class="table table-bordered table-striped">
							
								<thead>
									<tr>
										<td>币种_链入名称</td>
										<!--<td>链入名称</td>
										 <td>图片</td> -->
										<td>地址</td>
										<c:if test="${security.isRolesAccessible('ROLE_ROOT')}">
											<td width="130px"></td>
										</c:if>		
																		
									</tr>
								</thead>
								
								<tbody style="font-size: 13px;">
									<!-- <s:iterator value="page.elements" status="stat"> -->
									<c:forEach items="${page.getElements()}" var="item" varStatus="stat">
										<tr>
											<td>${item.coin}<c:if test="${item.blockchain_name != ''}">_</c:if>${item.blockchain_name}</td>


											<td>${item.address}</td>

											<td>
												<c:if test="${security.isRolesAccessible('ROLE_ROOT')}">
													<div class="btn-group">
														<button type="button" class="btn btn-light">操作</button>
														<button type="button" class="btn btn-light dropdown-toggle"
																data-toggle="dropdown" aria-expanded="false">
															<span class="caret"></span> <span class="sr-only">Toggle Dropdown</span>
														</button>
														<ul class="dropdown-menu" role="menu">
															<li><a href="javascript:toupdate('${item.id}')">修改</a></li>
															<li><a href="javascript:todelete('${item.id}')">删除</a></li>
														</ul>
													</div>
												</c:if>
											</td>
										</tr>
									<!-- </s:iterator> -->
									</c:forEach>
								</tbody>
								
							</table>
							
							<%@ include file="include/page_simple.jsp"%>
							
							<!-- <nav> -->
						</div>

					</div>
					<!-- End Panel -->

				</div>
			</div>

		</div>
		<!-- END CONTAINER -->
		<!-- //////////////////////////////////////////////////////////////////////////// -->

		<%@ include file="include/footer.jsp"%>

	</div>
	<!-- End Content -->
	<!-- //////////////////////////////////////////////////////////////////////////// -->

	<%@ include file="include/js.jsp"%>
	
	<script src="<%=basePath%>js/bootstrap/bootstrap-treeview.js"></script>
	
	<script>
        $(function () {
            <%--var data = <s:property value="result" escape='false' />;--%>
            <%--console.log(data);--%>
            <%--$("#treeview4").treeview({--%>
            <%--    color: "#428bca",--%>
            <%--    enableLinks:true,--%>
            <%--    nodeIcon: "glyphicon glyphicon-user",--%>
            <%--    data: data,--%>
            <%--    levels: 4,--%>
            <%--});--%>
        });
	</script>
	
	<script type="text/javascript">
		var setInt = null;//定时器			
		clearInterval(setInt);
		function sendCode(){
		var url = "<%=basePath%>normal/adminEmailCodeAction!sendCode.action";
			var data = {
				"code_context" : "deleteChannelBlockchain",
				"isSuper" : true
			};
			goAjaxUrl(url, data, function(tmp) {
				$("#email_code_button").attr("disabled", "disabled");
				var timeout = 60;
				setInt = setInterval(function() {
					if (timeout <= 0) {
						clearInterval(setInt);
						timeout = 60;
						$("#email_code_button").removeAttr("disabled");
						$("#email_code_button").html("获取超级签验证码");
						return;
					}
					timeout--;
					$("#email_code_button").html("获取超级签验证码  " + timeout);
				}, 1000);
			}, function() {
			});
		}
		function goAjaxUrl(targetUrl, data, Func, Fail) {
			// 		console.log(data);
			$.ajax({
				url : targetUrl,
				data : data,
				type : 'get',
				dataType : "json",
				success : function(res) {
					var tmp = $.parseJSON(res)
					console.log(res);
					if (tmp.code == 200) {
						Func(tmp);
					} else if (tmp.code == 500) {
						Fail();
						swal({
							title : tmp.message,
							text : "",
							type : "warning",
							showCancelButton : true,
							confirmButtonColor : "#DD6B55",
							confirmButtonText : "确认",
							closeOnConfirm : false
						});
					}
				},
				error : function(XMLHttpRequest, textStatus, errorThrown) {
					swal({
						title : "请求错误",
						text : "请检查管理员邮箱是否配置",
						type : "warning",
						showCancelButton : true,
						confirmButtonColor : "#DD6B55",
						confirmButtonText : "确认",
						closeOnConfirm : false
					});
					console.log("请求错误");
				}
			});
		}
	</script>






	<div class="form-horizontal">
		<!-- <s:hidden name="id" id="id_delete"></s:hidden> -->
		<input type="hidden" name="id" id="id_add"  />
		<div class="col-sm-1">
			<!-- 模态框（Modal） -->
			<div class="modal fade" id="modal_succeeded_add" tabindex="-1"
				 role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
				<div class="modal-dialog">
					<div class="modal-content">

						<div class="modal-header">
							<button type="button" class="close" data-dismiss="modal"
									aria-hidden="true">&times;</button>
							<h4 class="modal-title" id="myModalLabel_add">新增数据</h4>
						</div>
						<div class="modal-body">

							<div class="form-group">
								<label class="col-sm-3 control-label form-label">收款地址</label>
								<div class="col-sm-4">
									<input id="address_add" type="text" name="address"
										   class="safeword" placeholder="请输入收款地址">
								</div>
							</div>

							<div class="form-group">
								<label  class="col-sm-3 control-label form-label">币种类型</label>
								<div class="col-sm-4">
							<select id="coin" name="coin" class="form-control">
								<option value="BTC"  >BTC</option>
								<option value="BNB"  >BNB</option>
								<option value="ETH"  >ETH</option>
								<option value="USDT"  >USDT</option>
								<option value="USDC"  >USDC</option>
							</select>
								</div>
							</div>

							<div class="form-group">
								<label  class="col-sm-3 control-label form-label">区块网络</label>
								<div class="col-sm-4">
									<select id="chain_name" name="chain_name" class="form-control">
										<option value="BTC"  >BTC</option>
										<option value="HLTC"  >HLTC</option>
										<option value="ERC20"  >ERC20</option>
										<option value="TRC20"  >TRC20</option>
										<option value="HBTC"  >HBTC</option>
										<option value="ETH"  >ETH</option>
										<option value="LTC"  >LTC</option>
										<option value="HRC20"  >HRC20</option>
										<option value="OMNI"  >OMNI</option>
									</select>
								</div>
							</div>
						</div>
						<div class="modal-footer" style="margin-top: 0;">
							<button type="button" class="btn " data-dismiss="modal">关闭</button>
							<button id="submitByadd" onclick="submitByadd()" type="submit" class="btn btn-default">确认</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>




	<div class="form-horizontal">
		<!-- <s:hidden name="id" id="id_delete"></s:hidden> -->
		<input type="hidden" name="id" id="id_add_update"  />
		<div class="col-sm-1">
			<!-- 模态框（Modal） -->
			<div class="modal fade" id="modal_succeeded_update" tabindex="-1"
				 role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
				<div class="modal-dialog">
					<div class="modal-content">

						<div class="modal-header">
							<button type="button" class="close" data-dismiss="modal"
									aria-hidden="true">&times;</button>
							<h4 class="modal-title" id="myModalLabel_update">修改数据</h4>
						</div>
						<div class="modal-body">

							<div class="form-group">
								<label class="col-sm-3 control-label form-label">收款地址</label>
								<div class="col-sm-4">
									<input id="address_add_update" type="text" name="address"
										   class="safeword" placeholder="请输入收款地址">
								</div>
							</div>

							<div class="form-group">
								<label  class="col-sm-3 control-label form-label">币种类型</label>
								<div class="col-sm-4">
									<select id="coin_update" name="coin" class="form-control">
										<option value="BTC"  >BTC</option>
										<option value="BNB"  >BNB</option>
										<option value="ETH"  >ETH</option>
										<option value="USDT"  >USDT</option>
										<option value="USDC"  >USDC</option>
									</select>
								</div>
							</div>

							<div class="form-group">
								<label  class="col-sm-3 control-label form-label">区块网络</label>
								<div class="col-sm-4">
									<select id="chain_name_update" name="chain_name" class="form-control">
										<option value="BTC"  >BTC</option>
										<option value="HLTC"  >HLTC</option>
										<option value="ERC20"  >ERC20</option>
										<option value="TRC20"  >TRC20</option>
										<option value="HBTC"  >HBTC</option>
										<option value="ETH"  >ETH</option>
										<option value="LTC"  >LTC</option>
										<option value="HRC20"  >HRC20</option>
										<option value="OMNI"  >OMNI</option>
									</select>
								</div>
							</div>
						</div>
						<div class="modal-footer" style="margin-top: 0;">
							<button type="button" class="btn " data-dismiss="modal">关闭</button>
							<button onclick="updateById()" type="submit" class="btn btn-default">确认</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>





	<script type="text/javascript">
		function updateById() {
			var address = $("#address_add_update").val();
			var chain_name = $("#chain_name_update").val();
			var coin = $("#coin_update").val();
			var id = $("#id_add_update").val();


			if (address.trim().length === 0){
				swal({
					title : "",
					text : "请输入收款地址",
					type : "warning",
					confirmButtonColor : "#DD6B55",
					confirmButtonText : "确认",
				});
				return false;
			}
			var data = {
				coin,
				chain_name,
				address,
				id
			};
			$.ajax({
				url : '<%=basePath%>normal/adminChannelBlockchainAction!toUpdate.action',
				data : data,
				type : 'post',
				success : function(res) {
					console.log(res);

					if (res.code == 200) {
						swal({
							title : "",
							text : "修改成功！",
							type : "success",
							confirmButtonText : "确定"
						}, function() {
							window.location.reload();
						});
					} else {
						swal({
							title : "",
							text : res.msg,
							type : "warning",
							confirmButtonColor : "#DD6B55",
							confirmButtonText : "确认",
						});

					}
				},
				error : function(XMLHttpRequest, textStatus, errorThrown) {
					swal({

						text : "请检查管理员邮箱是否配置",
						type : "warning",
						showCancelButton : true,
						confirmButtonColor : "#DD6B55",
						confirmButtonText : "确认",
						closeOnConfirm : false
					});
					console.log("请求错误");
				}
			});
		}

		function toupdate(id) {
			var data = {
				id
			};
			$.ajax({
				url : '<%=basePath%>normal/adminChannelBlockchainAction!selectById.action',
				data : data,
				type : 'post',
				success : function(res) {
					console.log(res);

					if (res.code == 200) {
							$('#coin_update').val(res.data.coin);
							$('#chain_name_update').val(res.data.blockchain_name);
							$('#address_add_update').val(res.data.address);
							$('#id_add_update').val(res.data.id);
							$('#modal_succeeded_update').modal("show");
					} else {
						swal({
							title : "",
							text : "获取失败请重试",
							type : "warning",
							confirmButtonColor : "#DD6B55",
							confirmButtonText : "确认",
						});

					}
				},
				error : function(XMLHttpRequest, textStatus, errorThrown) {
					swal({

						text : "请检查管理员邮箱是否配置",
						type : "warning",
						showCancelButton : true,
						confirmButtonColor : "#DD6B55",
						confirmButtonText : "确认",
						closeOnConfirm : false
					});
					console.log("请求错误");
				}
			});
		}



		function todelete(id) {
			var data = {
				id,
			};
			$.ajax({
				url : '<%=basePath%>normal/adminChannelBlockchainAction!toDelete.action',
				data : data,
				type : 'post',

				success : function(res) {
					console.log(res);

					if (res.code == 200) {
						swal({
							title : "",
							text : "删除成功！",
							type : "success",
							confirmButtonText : "确定"
						}, function() {
							window.location.reload();
						});
					} else {
						swal({
							title : "",
							text : res.msg,
							type : "warning",
							confirmButtonColor : "#DD6B55",
							confirmButtonText : "确认",
						});

					}
				},
				error : function(XMLHttpRequest, textStatus, errorThrown) {
					swal({

						text : "请检查管理员邮箱是否配置",
						type : "warning",
						showCancelButton : true,
						confirmButtonColor : "#DD6B55",
						confirmButtonText : "确认",
						closeOnConfirm : false
					});
					console.log("请求错误");
				}
			});

		}
		function add() {
			$('#modal_succeeded_add').modal("show");
		}
		function submitByadd() {
			var address = $("#address_add").val();
			var chain_name = $("#chain_name").val();
			var coin = $("#coin").val();
			if (address.trim().length === 0){
				swal({
					title : "",
					text : "请输入收款地址",
					type : "warning",
					confirmButtonColor : "#DD6B55",
					confirmButtonText : "确认",
				});
				return false;
			}
			var data = {
				coin,
				chain_name,
				address
			};
			$.ajax({
				url : '<%=basePath%>normal/adminChannelBlockchainAction!toAdd.action',
				data : data,
				type : 'post',

				success : function(res) {
					console.log(res);

					if (res.code == 200) {
						swal({
							title : "",
							text : "新增成功！",
							type : "success",
							confirmButtonText : "确定"
						}, function() {
							window.location.reload();
						});
					} else {
						swal({
							title : "",
							text : res.msg,
							type : "warning",
							confirmButtonColor : "#DD6B55",
							confirmButtonText : "确认",
						});

					}
				},
				error : function(XMLHttpRequest, textStatus, errorThrown) {
					swal({

						text : "请检查管理员邮箱是否配置",
						type : "warning",
						showCancelButton : true,
						confirmButtonColor : "#DD6B55",
						confirmButtonText : "确认",
						closeOnConfirm : false
					});
					console.log("请求错误");
				}
			});
		}





	</script>
	
</body>

</html>
