<%@ page language="java" pageEncoding="utf-8" isELIgnored="false"%>
<%@taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<%@taglib prefix="fn" uri="http://java.sun.com/jsp/jstl/functions" %>
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

		<div class="row">


			<div class="col-md-12">
				<!-- Start Panel -->
				<div class="panel panel-default">

					<div class="panel-title">查询结果</div>

					<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
									 || security.isResourceAccessible('OP_NEWS_OPERATE')}">

						<a onclick="toAdd()" class="btn btn-light" style="margin-bottom: 10px">
							<i class="fa fa-pencil"></i>新增</a>

					</c:if>

					<div class="panel-body">
						<table class="table table-bordered table-striped">
							<thead>
							<tr>
								<td>标题</td>
								<td>分类</td>
								<td>第三方链接</td>
								<td>语言</td>
								<td>排序</td>
								<td>创建时间</td>
								<td width="130px"></td>
							</tr>
							</thead>
							<tbody>
							<!-- <s:iterator value="page.elements" status="stat"> -->
							<c:forEach items="${page.getElements()}" var="item" varStatus="stat">
								<input type="hidden" name="iconImg" id="iconImg" value = "${item.iconImg}"/>
								<tr>
									<td>${item.title}</td>
									<td>${item.class_name}</td>
									<td>${item.href}</td>

									<td>
										<c:choose>
											<c:when test="${item.lang == 'en'}">
												英文
											</c:when>
											<c:when test="${item.lang == 'vi'}">
												越南语
											</c:when>
											<c:when test="${item.lang == 'hi'}">
												印度语
											</c:when>
											<c:when test="${item.lang == 'id'}">
												印度尼西亚语
											</c:when>
											<c:when test="${item.lang == 'de'}">
												德语
											</c:when>
											<c:when test="${item.lang == 'fr'}">
												法语
											</c:when>
											<c:when test="${item.lang == 'ru'}">
												俄语
											</c:when>
											<c:when test="${item.lang == 'es'}">
												西班牙语
											</c:when>
											<c:when test="${item.lang == 'pt'}">
												葡萄牙语
											</c:when>
											<c:when test="${item.lang == 'it'}">
												意大利语
											</c:when>
											<c:when test="${item.lang == 'ms'}">
												马来西亚语
											</c:when>
											<c:when test="${item.lang == 'af'}">
												南非荷兰语
											</c:when>
											<c:when test="${item.lang == 'el'}">
												希腊语
											</c:when>
											<c:when test="${item.lang == 'tw'}">
												中文繁体
											</c:when>
											<c:when test="${item.lang == 'cn'}">
												中文简体
											</c:when>
											<c:when test="${item.lang == 'tr'}">
												土耳其语
											</c:when>
											<c:when test="${item.lang == 'ja'}">
												日语
											</c:when>
											<c:when test="${item.lang == 'ko'}">
												韩语
											</c:when>
											<c:when test="${item.lang == 'th'}">
												泰语
											</c:when>
											<c:when test="${item.lang == 'ph'}">
												菲律宾语
											</c:when>
											<c:when test="${item.lang == 'ar'}">
												阿拉伯语
											</c:when>
											<c:otherwise>
												中文繁体
											</c:otherwise>
										</c:choose>
									</td>

									<td>${item.sort}</td>
									<td>${item.create_time}</td>
									<td>
										<c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
															|| security.isResourceAccessible('OP_NEWS_OPERATE')}">
											<div class="btn-group">
												<button type="button" class="btn btn-light">操作</button>
												<button type="button" class="btn btn-light dropdown-toggle"
														data-toggle="dropdown" aria-expanded="false">
													<span class="caret"></span> <span class="sr-only">Toggle Dropdown</span>
												</button>
												<ul class="dropdown-menu" role="menu">
													<li><a href="javascript:toDelete('${item.uuid}')">删除</a></li>
												</ul>
											</div>
										</c:if>
									</td>

								</tr>

							</c:forEach>

							</tbody>
						</table>
						<%@ include file="include/page_simple.jsp"%>
						<nav>
					</div>
				</div>
			</div>
		</div>
	</div>


	<!-- 模态框 -->
	<div class="form-group">
		<form action=""
			  method="post" id="mainform">
			<input type="hidden" name="pageNo" id="pageNo" value="${pageNo}" />
			<input type="hidden" name="id" id="deleteid"/>
			<div class="col-sm-1 form-horizontal">
				<!-- 模态框（Modal） -->
				<div class="modal fade" id="modal_succeeded" tabindex="-1"
					 role="dialog" aria-labelledby="myModalLabel"
					 aria-hidden="true">
					<div class="modal-dialog">
						<div class="modal-content" >
							<div class="modal-header">
								<button type="button" class="close"
										data-dismiss="modal" aria-hidden="true">&times;</button>
								<h4 class="modal-title" id="myModalLabel">确认调整</h4>
							</div>
							<div class="modal-body">
								<div class="form-group" >
									<label for="input002" class="col-sm-3 control-label form-label">登录人资金密码</label>
									<div class="col-sm-4">
										<input id="login_safeword" type="password" name="login_safeword"
											   class="login_safeword" placeholder="请输入登录人资金密码" >
									</div>
								</div>
							</div>
							<div class="modal-footer" style="margin-top: 0;">
								<button type="button" class="btn "
										data-dismiss="modal">关闭</button>
								<button id="sub" type="submit"
										class="btn btn-default">确认</button>
							</div>
						</div>
						<!-- /.modal-content -->
					</div>
					<!-- /.modal -->
				</div>
			</div>
		</form>
	</div>



	<!-- 模态框 -->
	<div class="form-group">
		<form action=""
			  method="post" id="add_mainform">
			<div class="col-sm-1 form-horizontal">
				<!-- 模态框（Modal） -->
				<div class="modal fade" id="add_modal_succeeded" tabindex="-1"
					 role="dialog" aria-labelledby="myModalLabel"
					 aria-hidden="true">
					<div class="modal-dialog">
						<div class="modal-content" >
							<div class="modal-header">
								<button type="button" class="close"
										data-dismiss="modal" aria-hidden="true">&times;</button>
								<h4 class="modal-title" id="add_myModalLabel">确认添加</h4>
							</div>
							<div class="modal-body">
								<div class="form-group">
									<label for="input002" class="col-sm-3 control-label form-label">分类</label>
									<div class="col-sm-4 ">
										<div class="input-group">
											<select id="lang" name="class_id"
													class="form-control ">
												<c:forEach items="${classresult}" var="item">
												<option value="${item.uuid}">${item.class_name}</option>
												</c:forEach>
											</select>
										</div>
									</div>
								</div>




								<div class="form-group" >
									<label for="input002" class="col-sm-3 control-label form-label">标题</label>
									<div class="col-sm-4">
										<input id="title" type="text" name="title"
											   class="login_safeword" placeholder="请输入标题" >
									</div>
								</div>

								<div class="form-group" >
									<label for="input002" class="col-sm-3 control-label form-label">第三方跳转链接</label>
									<div class="col-sm-4">
										<input id="href" type="text" name="href"
											   class="login_safeword" placeholder="第三方跳转链接" >
									</div>
								</div>

								<div class="form-group" >
									<label for="input002" class="col-sm-3 control-label form-label">排序</label>
									<div class="col-sm-4">
										<input id="sort" type="number" name="sort"
											   class="login_safeword" placeholder="请输入排序" value="0">
									</div>
								</div>


							</div>
							<div class="modal-footer" style="margin-top: 0;">
								<button type="button" class="btn "
										data-dismiss="modal">关闭</button>
								<button id="addsub" type="submit"
										class="btn btn-default">确认</button>
							</div>
						</div>
						<!-- /.modal-content -->
					</div>
					<!-- /.modal -->
				</div>
			</div>
		</form>
	</div>

	<%@ include file="include/footer.jsp"%>

</div>
<!-- End Content -->
<!-- //////////////////////////////////////////////////////////////////////////// -->

<%@ include file="include/js.jsp"%><script src="<%=basePath%>js/bootstrap/bootstrap-treeview.js"></script>
<script>
</script>


<script type="text/javascript">
	function toAdd(){
		$('#add_mainform').attr("action","<%=basePath%>/invest/expert/toAdd.action");
		$('#add_modal_succeeded').modal("show");
	}


	function toDelete(id){
		$('#deleteid').val(id);
		console.log(id)
		$('#pageNo').val(pageNo);
		$('#myModalLabel').html("删除");
		$('#mainform').attr("action","<%=basePath%>/invest/expert/delete.action");
		$('#modal_succeeded').modal("show");
	}

	$(function() {
		$('#startTime').datetimepicker({
			format : 'yyyy-mm-dd hh:ii:00',
			minuteStep:1,
			language : 'zh',
			weekStart : 1,
			todayBtn : 1,
			autoclose : 1,
			todayHighlight : 1,
			startView : 2,
			clearBtn : true
		});
		$('#endTime').datetimepicker({
			format : 'yyyy-mm-dd hh:ii:00',
			minuteStep:1,
			language : 'zh',
			weekStart : 1,
			todayBtn : 1,
			autoclose : 1,
			todayHighlight : 1,
			startView : 2,
			clearBtn : true
		});

	});
</script>
</body>
</html>