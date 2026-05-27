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
<style>
    .sweet-alert{
        top: 25%;
    }
    .productDialog {
        display: flex;
        /*align-items: center;*/
    }
    .productDialog .left {
        width: 50%;
        margin-right: 10px;
    }
    .productDialog .right {
        width: 50%;
    }

    .disabled {
        background-color: #f2f2f2 !important;
        color: #999 !important;
    }
    ::-webkit-scrollbar-track {
        background-color: #F5F5F5;
    }

    ::-webkit-scrollbar {
        width: 6px;
        background-color: #F5F5F5;
    }

    ::-webkit-scrollbar-thumb {
        background-color: #999;
    }
    .productDialogBodyBox {
        padding: 20px;
        border: 1px solid #ccc;
        height: 565px;
        overflow: auto;
    }
    .productDialogBody {
        display: flex;
        padding: 20px;
        border: 1px solid #ccc;
    }
    .productDialogBody .productRight {
        display: flex;
        flex-direction: column;
    }
    .productDialogBody .productImg {
        margin-right: 10px;
    }
    .productDialogBody .productImg img {
        width: 80px;
        height: 80px;
    }

    .productDialogBody .productName {
        font-size: 14px;
        margin-bottom: 10px;

    }
    .productDialogBody .productBox {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .productDialogBody .dialogPrice {
        display: flex;
    }
    .productDialogBody .productNumberBox {
        display: flex;
        align-items: center;
        justify-content: end;
    }
    .productDialogBody .productNumberBox input {
        width: 60%;
        height: 20px;
    }
    .customerDialogBody {
      padding: 20px;
    }
    .customerDialogBody .customerItem {
        margin-bottom: 10px;
        font-size: 14px;
    }
    .customerSelect {
        -webkit-appearance: none;
        background-color: #fff;
        background-image: none;
        border-radius: 4px;
        border: 1px solid #dcdfe6;
        box-sizing: border-box;
        color: #606266;
        display: inline-block;
        font-size: inherit;
        height: 30px;
        line-height: 30px;
        outline: none;
        padding: 0 15px;
        transition: border-color .2s cubic-bezier(.645,.045,.355,1);
        width: 100%;
    }
    .customerItem input {
        -webkit-appearance: none;
        background-color: #fff;
        background-image: none;
        border-radius: 4px;
        border: 1px solid #dcdfe6;
        box-sizing: border-box;
        color: #606266;
        display: inline-block;
        font-size: inherit;
        height: 30px;
        line-height: 30px;
        outline: none;
        padding: 0 15px;
        transition: border-color .2s cubic-bezier(.645,.045,.355,1);
        width: 100%;
    }
    .customerItem textarea {
        -webkit-appearance: none;
        background-color: #fff;
        background-image: none;
        border-radius: 4px;
        border: 1px solid #dcdfe6;
        box-sizing: border-box;
        color: #606266;
        display: inline-block;
        font-size: inherit;
        outline: none;
        padding: 0 15px;
        transition: border-color .2s cubic-bezier(.645,.045,.355,1);
        width: 100%;
    }
    #timePicker {
        width: 200px;
        margin: 0 20px;
    }

    .modalProductFooter {
        display: flex;
        padding: 0 20px;
    }
    .modalProductFooter .methodText {
        margin-right: 10px;
        /*width: -webkit-fill-available;*/
    }
    .modalProductFooter .method {
        display: flex;
        align-items: center;
    }
    .modal-header {
        display: flex;
        justify-content: space-between;
    }
</style>
<body>
<%@ include file="include/loading.jsp"%>
<%-- 	<%@ include file="include/top.jsp"%> --%>
<%-- 	<%@ include file="include/menu_left.jsp"%> --%>


<!-- START CONTENT -->
<div class="ifr-dody">


    <!-- START CONTAINER -->
    <div class="ifr-con">
        <h3>POS下单</h3>
        <!-- //////////////////////////////////////////////////////////////////////////// -->
        <!-- START queryForm -->
        <%@ include file="include/alert.jsp"%>
        <div class="row">
            <div class="col-md-12">
                <div class="panel panel-default">

                    <div class="panel-title">查询条件</div>
                    <div class="panel-body">

                        <form class="form-horizontal" action="<%=basePath%>/mall/pos/list.action" method="post"
                              id="queryForm">
                            <input type="hidden" name="pageNo" id="pageNo"
                                   value="${pageNo}">
                            <input type="hidden" name="messages" id="messages"
                                   value="${messages}">
                            <div class="col-md-12 col-lg-2">
                                <fieldset>
                                    <div class="control-group">
                                        <div class="controls">
                                            <input id="goodName" name="goodName" class="form-control"
                                                   placeholder="商品名称" value = "${goodName}"/>
                                        </div>
                                    </div>
                                </fieldset>
                            </div>
                            <div class="col-md-12 col-lg-2">
                                <fieldset>
                                    <div class="control-group">
                                        <div class="controls">
                                            <input id="goodId" name="goodId" class="form-control"
                                                   placeholder="商品ID" value = "${goodId}"/>
                                        </div>
                                    </div>
                                </fieldset>
                            </div>

                            <div class="col-md-12 col-lg-2">
                                <fieldset>
                                    <div class="control-group">
                                        <div class="controls">
                                            <input id="sellerId" name="sellerId" class="form-control"
                                                   placeholder="店铺ID" value = "${sellerId}"/>
                                        </div>
                                    </div>
                                </fieldset>
                            </div>

                            <div class="col-md-12 col-lg-2">
                                <fieldset>
                                    <div class="control-group">
                                        <div class="controls">
                                            <input id="sellerName" name="sellerName" class="form-control"
                                                   placeholder="店铺名称" value = "${sellerName}"/>
                                        </div>
                                    </div>
                                </fieldset>
                            </div>



                            <div class="col-md-12 col-lg-2">
                                <button type="submit" class="btn btn-light btn-block">查询</button>
                            </div>

                        </form>

                    </div>

                </div>
            </div>
        </div>
        <!-- END queryForm -->
        <!-- //////////////////////////////////////////////////////////////////////////// -->


        <div class="row">


            <div class="col-md-12">
                <!-- Start Panel -->
                <div class="panel panel-default">

                    <div class="panel-title">查询结果</div>
                    <c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
									 || security.isResourceAccessible('OP_GOODS_OPERATE')}">
                        <a  id="shelfBatch" class="btn btn-light" style="margin-bottom: 12px"><i
                                class="fa fa-pencil"></i>批量下单</a>
                    </c:if>

                    <div class="panel-body">
                        <table class="table table-bordered table-striped">
                            <thead>
                            <tr>
                                <td>
                                    <input id="selAll" type="checkbox" />
                                </td>
                                <td>ID</td>
                                <td>店铺ID</td>
                                <td>商品ID</td>
                                <td>店铺名称</td>
                                <td>商品名称</td>
                                <td>商品图</td>
                                <td>销售价格</td>
                                <td>操作</td>
                            </tr>
                            </thead>
                            <tbody>
                            <!-- <s:iterator value="page.elements" status="stat"> -->

                            <c:forEach items="${page.getElements()}" var="item" varStatus="stat">
                                <input type="hidden" name="iconImg" id="iconImg" value = "${item.iconImg}"/>
                                <tr>
                                    <td style="width: 50px;align-content: center;">
                                        <input name="checkbox" type="checkbox" value="${item.id}">
                                    </td>
                                    <td style="width: 160px; align-content: center;">${item.ID}</td>
                                    <td style="width: 160px; align-content: center;">${item.USERCODE}</td>
                                    <td style="width: 160px; align-content: center;">${item.goodsId}</td>
                                    <td style="width: 160px; align-content: center;">${item.sellerName}</td>
                                    <td style="width: 320px; align-content: center;">
                                            ${item.name}
                                    </td>
                                    <td style="width: 120px;text-align: center; align-content: center;">
                                            <img src="${item.cover}" width="120" height="120">
                                    </td>
<%--                                    <td style="width: 160px;">${item.categoryId}</td>--%>
                                    <td style="width: 160px; align-content: center;">${item.sellingPrice}</td>
                                    <td style="width: 160px; align-content: center;text-align: center;">
                                        <c:if test="${security.isRolesAccessible('ROLE_ROOT,ROLE_ADMIN')
															|| security.isResourceAccessible('OP_GOODS_OPERATE')}">
                                            <button type="submit" class="btn btn-success selectGoods">下单</button>
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
                <!-- End Panel -->

            </div>
        </div>

    </div>

    <div class="modal" id="myModalProduct">
        <div class="modal-dialog" style="width: 994px">
            <div class="modal-content">
                <div class="modal-header">
                    <h4 class="modal-title">确认订单</h4>
                    <button type="button" class="close" data-dismiss="modal">&times;</button>
                </div>
                <div class="modal-body productDialog">
                    <div class="left">
                        商品信息
                        <div class="productDialogBodyBox">
                            <div class="productDialogBody">
                                <div class="productImg">
                                    <img src="https://hetao-shop-test.s3.amazonaws.com/goods/2023-09-17/4bda5d0b-41f2-40a3-a49a-5dced4982cfb.jpeg" alt="">
                                </div>
                                <div class="productRight">
                                    <div class="productName">eweqeqe2ewqeqwe</div>
                                    <div class="productBox">
                                        <div class="dialogPrice">$ <span id="dialogPrice">24.96</span> </div>
                                        <div class="productNumberBox">
                                            × <input type="number" value="1">
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>

                    </div>
                    <div class="right">
                    顾客信息
                        <div class="customerDialogBody">
                            <div class="customerItem">
                                <select name="guestUsers" id="guestUsers" placeholder="请选择" class="customerSelect">
                                    <option value="0">请选择下单账号</option>
                                    <c:forEach items="${guestUsers}" var="item" varStatus="stat">
                                        <option value="${item.id}">${item.username}</option>
                                    </c:forEach>
                                </select>
                            </div>

                            <div class="customerItem addressLibrary" style="display: none">
                                <select name="address" id="addressLibrary" placeholder="请选择" class="customerSelect">
                                    <option value="0">请选择下单地址</option>
                                </select>
                            </div>


                            <div class="customerItem">
                                姓名
                                <input id="username" class="form-control" type="text" disabled>
                            </div>
                            <div class="customerItem">
                                电子邮件
                                <input id="email" class="form-control" type="text" disabled>
                            </div>
                            <div class="customerItem">
                                手机号
                                <input id="mobile" class="form-control" type="text" disabled>
                            </div>
                            <div class="customerItem">
                                国家
                                <input id="country" class="form-control" type="text" disabled>
                            </div>
                            <div class="customerItem">
                                州
                                <input class="form-control" id="province" type="text" disabled>
                            </div>
                            <div class="customerItem">
                                城市
                                <input class="form-control" id="city" type="text" disabled>
                            </div>
                            <div class="customerItem">
                                邮政编码
                                <input class="form-control" id="zipcode" type="number" disabled>
                            </div>
                            <div class="customerItem">
                                地址
                                <textarea class="form-control" id="homeaddress" cols="25" rows="4" disabled></textarea>
                            </div>
                        </div>
                    </div>
                </div>
                <input type="hidden" id="partyId">
                <input type="hidden" id="addressId">
                <div class="modalProductFooter">
                    <div class="method">
                        <div class="methodText">下单方式: </div>
                        <div >
                            <select name="ordermode" id="ordermode" placeholder="请选择" class="customerSelect" style="width: 150px;">
                                <option value="1" selected>实时</option>
                                <option value="2">定时</option>
                            </select>
                        </div>

                        <div class="methodText" style="margin-left: 20px;">下单时间: </div>
                       <div>
                           <input type="datetime-local" id="datePicker" class="customerSelect"  style="margin: 0 20px; ">
                       </div>

                    </div>
                </div>

                <div class="modal-footer">
                    <button id="submitOrder" type="button" class="btn btn-primary" >确认下单</button>
                </div>
            </div>
        </div>
    </div>


    <%@ include file="include/footer.jsp"%>

</div>
<!-- End Content -->
<!-- //////////////////////////////////////////////////////////////////////////// -->

<%@ include file="include/js.jsp"%><script src="<%=basePath%>js/bootstrap/bootstrap-treeview.js"></script>
<script>
</script>


<script type="text/javascript">
    function initParams() {
        $('#username').val('');
        $('#email').val('');
        $('#country').val('');
        $('#province').val('');
        $('#zipcode').val('');
        $('#homeaddress').val('');
        $('#mobile').val('');
        $('#city').val('');
        $('#partyId').val('');
        $('#addressId').val('');
    }
    $('#addressLibrary').change(function(){
        var selectedAddress = $(this).val();
        if (selectedAddress == 0){
            initParams();
            return;
        }
        $.ajax({
            url: "<%=basePath%>mall/pos/address_info.action?id=" + selectedAddress,
            type: 'GET',
            success: function (data) {
                if (data.code == '1'){
                  var info = data.data;
                  $('#username').val(info.contacts);
                  $('#email').val(info.email);
                  $('#country').val(info.country);
                  $('#province').val(info.province);
                  $('#zipcode').val(info.postcode);
                  $('#homeaddress').val(info.address);
                  $('#mobile').val(info.phone);
                  $('#city').val(info.city);
                  $('#partyId').val(info.partyId);
                  $('#addressId').val(info.id);
                }else{
                    errorMsg("获取失败,请重试");
                    return;
                }
            }
        });
    });

    $('#guestUsers').change(function(){
        var partyId = $(this).val();
        var firstOption = $('#addressLibrary option:first');
        $('#addressLibrary').find('option').not(':first').remove();
        $('#addressLibrary').append(firstOption);
        if (partyId == 0){
            $('.addressLibrary').hide();
            initParams();
            return;
            return;
        }else{
            $.ajax({
                url: "<%=basePath%>mall/pos/address.action?id=" + partyId,
                type: 'GET',
                success: function (data) {
                    if (data.code == '1'){
                        data.data.forEach(function(element) {
                            var newOption = $('<option>').text(element.contacts + '-' +element.country +  '-' + element.phone).val(element.id);
                            $('#addressLibrary').append(newOption);
                        });
                        $('.addressLibrary').show();
                    }else{
                        errorMsg("该账号下最少要有一个收货地址");
                        return;
                    }

                }
            });
        }
    });



    $('.selectGoods').on('click', function () {
        initParams();
        var $tr = $(this).closest('tr')
        var itemID = $tr.find('td:nth-child(2)').html()
        var itemName = $tr.find('td:nth-child(6)').html()
        var sekkingPrice = $tr.find('td:nth-child(8)').html()
        var imageUrl = $tr.find('td:nth-child(7) img').attr('src')
        var selectedItems = [{productName: itemName, price: sekkingPrice, imageUrl,itemID}]
        renderProduct(selectedItems)
    })

    //提交订单
    $('#submitOrder').on('click', function () {
        var ShopingCart = getShopingCart();
        console.log(ShopingCart)
        if (!ShopingCart){
            errorMsg("商品数量有误");
            return;
        }
        var username = $('#username').val();
        var email = $('#email').val();
        var country = $('#country').val();
        var province = $('#province').val();
        var zipcode = $('#zipcode').val();
        var homeaddress = $('#homeaddress').val();
        var ordermode = $('#ordermode').val();
        var datePicker = $('#datePicker').val();
        var mobile = $('#mobile').val();
        var city = $('#city').val();
        var addressId = $('#addressId').val();
        var partyId = $('#partyId').val();
        if(!username || username.trim() === '') {
            errorMsg("请输入收货人姓名");
            return;
        }

        if(!email || email.trim() === '') {
            errorMsg("请输入邮箱");
            return;
        }

        if(!mobile || mobile.trim() === '') {
            errorMsg("请输入收货人手机号");
            return;
        }

        if (!validateEmail(email)){
            errorMsg("邮箱不格式不正确");
            return;
        }

        if(!country || country.trim() === '') {
            errorMsg("请输入国家");
            return;
        }

        if(!province || province.trim() === '') {
            errorMsg("请输入省份");
            return;
        }

        if(!city || city.trim() === '') {
            errorMsg("请输入城市");
            return;
        }

        if(!zipcode || zipcode === '') {
            errorMsg("请输入邮编");
            return;
        }

        var zipcodePattern = /^[0-9]+$/;

        if (!zipcodePattern.test(zipcode)){
            errorMsg("邮编格式不正确");
            return;
        }

        if(!homeaddress || homeaddress.trim() === '') {
            errorMsg("请输入地址");
            return;
        }
        if (ordermode == 2){
            if(!datePicker) {
                errorMsg("请设置下单时间");
                return;
            }
        }
        var formData = {
                partyId,
                addressId,
                ordermode,
                datePicker,
                order: ShopingCart
        };
        var formDataJSON = JSON.stringify(formData);
        $.ajax({
            url: "<%=basePath%>mall/pos/create_task.action",
            type: 'POST',
            contentType: 'application/json',
            data: formDataJSON,
            success: function (data) {
                if (data.code == -1) {
                    errorMsg(data.msg);
                    return;
                }
                swal({
                    title: '下单成功',
                    text: "",
                    type: "success",
                    confirmButtonText: "确认",
                }, function() {
                    location.reload();
                });

            }
        });


    });
    $('#shelfBatch').click(function () {

        var selectedItems = []
        $('input[name="checkbox"]:checked').each(function () {
            var $tr = $(this).closest('tr')
            var itemID = $tr.find('td:nth-child(2)').text()
            var itemName = $tr.find('td:nth-child(6)').text()
            var sekkingPrice = $tr.find('td:nth-child(8)').text()
            var imageUrl = $tr.find('td:nth-child(7) img').attr('src')
            selectedItems.push({ productName: itemName, price: sekkingPrice, imageUrl: imageUrl,itemID})
        })
        if (selectedItems.length == 0){
            errorMsg("最少选择一个商品");
            return false;
        }

        renderProduct(selectedItems)
    })
    function getShopingCart(){
        var isValid = [];
        $('.productNumberBox').each(function() {
            var dataId = $(this).data('id');
            var quantity = $(this).find('#num').val();

            if (!quantity || quantity <= 0){
                isValid = false;
                return false;
            }
            if (!(/^\d+$/.test(quantity) && parseInt(quantity, 10) > 0)){
                isValid = false;
                return false;
            }
            const goods = { id: dataId, count: quantity };
            isValid.push(goods);
        });
        return isValid;
    }

    function validateEmail(email) {
        var pattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        return pattern.test(email);
    }
    function errorMsg(msg){
        swal({
            title : msg,
            text : "",
            type : "warning",
            confirmButtonText : "确认",
        });
    }
    function renderProduct (selectedItems) {
        var modalContent = '';
        selectedItems.forEach(function(item) {
            modalContent += '<div class="productDialogBody">' +
                '<div class="productImg">' +
                '<img src="' + item.imageUrl + '" alt="' + item.productName + '">' +
                '</div>' +
                '<div class="productRight">' +
                '<div class="productName">' + item.productName + '</div>' +
                '<div class="productBox">' +
                '<div class="dialogPrice">$ <span id="dialogPrice">' + item.price + '</span> </div>' +
                '<div class="productNumberBox" data-id="'+item.itemID+'">' +
                '× <input id="num" type="number" value="1">' +
                '</div>' +
                '</div>' +
                '</div>' +
                '</div>';
        });
        $('#myModalProduct .productDialogBodyBox').html(modalContent)
        $('#myModalProduct').modal('show')
    }



    $('#datePicker').prop('disabled', true).addClass('disabled');

    // 监听选择框变化事件
    $('#ordermode').change(function() {
        console.log('$(this).val()', $(this).val())
        if ($(this).val() === '2') {
            $('#datePicker').prop('disabled', false).removeClass('disabled');
        } else {

            $('#datePicker').prop('disabled', true).addClass('disabled');
        }
    });
    <%--setTimeout(function() {--%>
    <%--	start();--%>
    <%--}, 100);--%>

    <%--function start(){--%>
    <%--	var img = $("#iconImg").val();--%>
    <%--	var show_img = document.getElementById('show_img');--%>
    <%--	show_img.src="<%=basePath%>normal/showImg.action?imagePath="+img;--%>
    <%--}--%>

    function toDelete(id,pageNo){
        $('#id').val(id);
        $('#pageNo').val(pageNo);
        $('#myModalLabel').html("删除");
        $('#mainform').attr("action","<%=basePath%>mall/goods/delete.action");

        $('#modal_succeeded').modal("show");

    }

    function addFakeComment(sellerId,creditScore){
        $("#sellerId1").val(sellerId);
        $("#NowCreditScore").val(creditScore);
        $('#modal_set2').modal("show");
    }


    function onsucceeded(id) {
        // var session_token = $("#session_token").val();
        // $("#session_token_success").val(session_token);
        $("#sellerGoodsId").val(id);
        $('#modal_set').modal("show");
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



    $("#selAll").on("click", function(){
        var che=$("#selAll").prop('checked');
        if(che){
            $("input[name='checkbox']").prop('checked',true);
        } else {
            $("input[name='checkbox']").prop('checked',false);
        }
    })


    $("input[name='checkbox']").on("click", function(){
        var setFalse=false;// 默认不给全选按钮设置false
        $.each($("input[name='checkbox']"),function(index,item){
            // 如果在普通多选框的循环中发现有false,就需要将全选按钮设置为false
            if(item.checked==false){
                setFalse=true;
            }
        })
        if(setFalse){
            $("#selAll").prop('checked',false);
        } else {// 如果普通按钮都为true, 则全选按钮也赋值为true
            $("#selAll").prop('checked',true);
        }
    })

</script>
</body>
</html>