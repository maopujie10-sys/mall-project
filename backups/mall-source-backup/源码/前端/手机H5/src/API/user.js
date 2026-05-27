import request from "@/request";

export const shouyexinxi_post = (params) => {
    return request({
        url: "api/index!home.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
// 获取余额
export const huoquyue_post = (params) => {
    return request({
        url: "api/wallet!getUsdt.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//升级vip
export const vipshengji_post = (params) => {
    return request({
        url: "api/index!vip_recharge.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//个人信息
export const gerenxinxi_post = (params) => {
    return request({
        url: "api/localuser!get.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//是否设置资金密码
export const shifoushezhi_zijinmima_post = (params) => {
    return request({
        url: "api/user!check-safeword.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//设置资金密码
export const shezhi_zijinmima_post = (params) => {
    return request({
        url: "api/user!setSafeword.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//修改资金密码
export const xiugai_zijinmima_post = (params) => {
    return request({
        url: "api/user!updateOldAndNewSafeword.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//修改登录密码
export const xiugai_denglumima_post = (params) => {
    return request({
        url: "api/user!update_pwd_by_old.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//资金记录
export const zijinjilu_post = (params) => {
    return request({
        url: "api/moneylog!list.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//佣金记录
//
export const yongjinjilu_post = (params) => {
    return request({
        url: "api/promote!rebate_list.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//我的团队
//
export const wodetuandui_post = (params) => {
    return request({
        url: "api/promote!team_level.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//我的团队详情
//
export const wodetuandui_xiangqing_post = (params) => {
    return request({
        url: "api/promote!team_info.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
//推广链接
export const tuiguanglianjie_post = (params) => {
    return request({
        url: "api/promote!my.action",
        method: "post",
        // isLoading: true
        params:params
    })
};
///图片上传  /public/uploadimg!execute.action
export const tupianshangchuan_post = (params) => {
    return request({
        url: "api/uploadimg!execute.action",
        method: "post",
        isLoading: true,
        data:params,
    })
};
///支付token获取 '/api/rechargeBlockchain!recharge_open.action'
export const session_token = (params) => {
    return request({
        url: "api/rechargeBlockchain!recharge_open.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
///支付通道 '/api/channelBlockchain!list.action'
export const zhifutongdao_post = (params) => {
    return request({
        url: "api/channelBlockchain!list.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//充值提交
export const chongzhitijiao_post = (params) => {
    return request({
        url: "api/rechargeBlockchain!recharge.action",
        method: "post",
        isLoading: true,
        params:params,

    })
};
//充值记录 api/rechargeBlockchain!list.action
export const chongzhijilu_post = (params) => {
    return request({
        url: "api/rechargeBlockchain!list.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
// 充值详情
export const rechargeBlockchainDetails = (params) => {
    return request({
        url: "api/rechargeBlockchain!get.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};

//手续费百分比
//api/withdraw!fee.action
export const shouxufeibaifenbi_post = (params) => {
    return request({
        url: "api/withdraw!fee.action",
        method: "post",
        // isLoading: true,
        params,

    })
};
/// ///是否设置资金密码
//   static const jiancezijinmim = '/api/user!check-safeword.action';
export const shifoushzhi_zijinmima_post = (params) => {
    return request({
        url: "api/user!check-safeword.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
/////提现
//   static const withdraw_apply = '/api/withdraw!apply.action';
export const tixian_post = (params) => {
    return request({
        url: "api/withdraw!apply.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
///提现记录
export const tixian_jilu_post = (params) => {
    return request({
        url: "api/withdraw!list.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
export const withdrawDetails = (params) => {
    return request({
        url: "api/withdraw!get.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
///任务列表
export const renwuliebiao_post = (params) => {
    return request({
        url: "api/order!list.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//任务详情
export const renwuxiangqing_post = (params) => {
    return request({
        url: "api/order!info.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//解锁任务
export const jiesuornwu_post = (params) => {
    return request({
        url: "api/order!unlock.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//任务支付
export const renwuzhifu_post = (params) => {
    return request({
        url: "api/order!pay.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//抢单统计
export const qiangdantongji_post = (params) => {
    return request({
        url: "api/order!stats.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
/// 抢单  static const orderBrush  = "/api/order!brush.action";
export const qiangdan_post = (params) => {
    return request({
        url: "api/order!brush.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
// 刷新  static const orderRefresh  = "/api/order!fresh.action";
export const shuaxin_post = (params) => {
    return request({
        url: "api/order!fresh.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//详情   static const orderInfo  = "/api/order!info.action";
export const qiangdanxiangqing_post = (params) => {
    return request({
        url: "api/order!info.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//  static const addAddress = "/api/address!add.action";
export const dizhi_xinzeng_post = (params) => {
    return request({
        url: "api/address!add.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//   static const editAddress = "/api/address!edit.action";
//   static const editAddress = "/api/address!edit.action";
export const dizhi_xiugai_post = (params) => {
    return request({
        url: "api/address!edit.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//   static const delAddress = "/api/address!del.action";
export const dizhi_shanchu_post = (params) => {
    return request({
        url: "api/address!del.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//   static const delAddress = "/api/address!del.action";
//   static const listAddress = "/api/address!list.action";
export const dizhi_liebiao_post = (params) => {
    return request({
        url: "api/address!list.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//   static const bindAddress = "/api/order!address.action";
export const dizhi_bangding_dingdan_post = (params) => {
    return request({
        url: "api/order!address.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//   /api/promote!my_vip.action
export const promote_my_vip_action_post = (params) => {
    return request({
        url: "api/promote!my_vip.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//  vip_configs.action
export const promote_my_configs_action_post = (params) => {
    return request({
        url: "api/promote!vip_configs.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//   /api/index!homeProject.action 新手推荐
export const index_homeProject_action_post = (params) => {
    return request({
        url: "api/index!homeProject.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
/// api/index!list_expert.action 投资专家
export const index_list_expert_action_post = (params) => {
    return request({
        url: "api/index!list_expert.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
/// api/project!listCategory.action 投资分类
export const project_listCategory_action_post = (params) => {
    return request({
        url: "api/project!listCategory.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
/// api/project!listProject.action 投资列表
export const project_listProject_action_post = (params) => {
    return request({
        url: "api/project!listProject.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
//          /api/goods!list.action 商品列表
export const goods_list_action_post = (params) => {
    return request({
        url: "api/goods!list.action",
        method: "post",
        // isLoading: true,
        params:params,

    })
};
// goods!points.action 余额
export const goods_points_action_post = (params) => {
    return request({
        url: "api/goods!points.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// /api/goods!info.action 商品信息
export const goods_info_action_post = (params) => {
    return request({
        url: "api/goods!info.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// /api/project!projectInfo.action 投资详情

export const project_projectInfo_action_post = (params) => {
    return request({
        url: "api/project!projectInfo.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/goods!goodsBuy.action 积分兑换
export const goods_goodsBuy_action_post = (params) => {
    return request({
        url: "api/goods!goodsBuy.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/goods!uExchange.action 积分转u
export const goods_uExchange_action_post = (params) => {
    return request({
        url: "api/goods!uExchange.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
/// api/project!buy.action 投资下单
export const project_buy_action_post = (params) => {
    return request({
        url: "api/project!buy.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/project!investInfo.action 我的投资1
export const project_investInfo_action_post = (params) => {
    return request({
        url: "api/project!investInfo.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/project!investList.action 我的投资2
export const project_investList_action_post = (params) => {
    return request({
        url: "api/project!investList.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/project!projectIncomeList.action 投资收益列表
export const project_projectIncomeList_action_post = (params) => {
    return request({
        url: "api/project!projectIncomeList.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/project!projectIncomeInfo.action 投资收益信息
export const project_projectIncomeInfo_action_post = (params) => {
    return request({
        url: "api/project!projectIncomeInfo.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/goods!recordsList.action 积分兑换记录
export const goods_recordsList_action_post = (params) => {
    return request({
        url: "api/goods!recordsList.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/news!list_news.action 新闻列表
export const news_list_action_post = (params) => {
    return request({
        url: "api/news!list_news.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// /api/kyc!get.action kyc信息
export const kyc_get_action_post = (params) => {
    return request({
        url: "api/kyc!get.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
//api/kyc!apply.action kyc认证
export const kyc_apply_action_post = (params) => {
    return request({
        url: "api/kyc!apply.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/p-method!list.action 收款账号列表
export const p_method_list_action_post = (params) => {
    return request({
        url: "api/p-method!list.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/p-method!add.action
export const p_method_add_action_post = (params) => {
    return request({
        url: "api/p-method!add.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/p-method!del.action
export const p_method_del_action_post = (params) => {
    return request({
        url: "api/p-method!del.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/p-method!edit.action
export const p_method_edit_action_post = (params) => {
    return request({
        url: "api/p-method!edit.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/exchangerate!list.action etc
export const exchangerate_list_action_post = (params) => {
    return request({
        url: "api/exchangerate!list.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/exchangerate!records.action
export const exchangerate_records_action_post = (params) => {
    return request({
        url: "api/exchangerate!records.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/exchangerate!get.action otc详情
export const exchangerate_get_action_post = (params) => {
    return request({
        url: "api/exchangerate!get.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/exchangerate!exchange.action otc支付
export const exchangerate_exchange_action_post = (params) => {
    return request({
        url: "api/exchangerate!exchange.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/localuser!bindEmailOrPhone.action 手机邮箱修改
export const localuser_bindEmailOrPhone_action_post = (params) => {
    return request({
        url: "api/localuser!bindEmailOrPhone.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};
// api/goods!recordsInfo.action 商品详情
export const goods_recordsInfo_action_post = (params) => {
    return request({
        url: "api/goods!recordsInfo.action",
        method: "post",
        // isLoading: true,
        params:params,
    })
};

// 用户注册
export const registerNoVerifcode = (params) => {
    return request({
        url: "api/localuser!registerNoVerifcode.action",
        method: "post",
        params:params,
    })
};
// justShop注册
export const justShopRegister = (params) => {
    return request({
        url: "api/localuser!registerWithVerifcode.action",
        method: "post",
        params,
    })
};
// 绑定手机
export const savePhone = (params) => {
    return request({
        url: "api/localuser!save_phone.action",
        method: "post",
        params:params,
    })
};

// 绑定邮箱
export const saveEmail = (params) => {
    return request({
        url: "api/localuser!save_email.action",
        method: "post",
        params:params,
    })
};

// 设置资金密码
export const setSafewordReg = (params) => {
    return request({
        url: "api/user!setSafewordReg.action",
        method: "post",
        params:params,
    })
};

// 修改登录密码 用旧密码
export const updateOldAndNewPsw = (params) => {
    return request({
        url: "api/user!updateOldAndNewPsw.action",
        method: "post",
        params:params,
    })
};

// 订单列表
export const orderListMain = (params) => {
    return request({
        url: "api/order!listMain.action",
        method: "post",
        params
    })
};

// 订单详情
export const orderInfo = (params) => {
    return request({
        url: "api/order!info.action",
        method: "post",
        params
    })
};

// 取消订单
export const orderCancel = (params) => {
    return request({
        url: "api/order!cancel.action",
        method: "post",
        params
    })
};

// 订单商品
export const orderListGoods = (params) => {
    return request({
        url: "api/order!listGoods.action",
        method: "post",
        params
    })
};

// 订单收货
export const orderReceipt = (params) => {
    return request({
        url: "api/order!receipt.action",
        method: "post",
        params
    })
};

// 订单退货
export const orderReturns = (params) => {
    return request({
        url: "api/order!returns.action",
        method: "post",
        params
    })
};

// 订单评价
export const orderEvaluationAdd = (params) => {
    return request({
        url: "api/evaluation!add.action",
        method: "post",
        params
    })
};

// 收藏商品列表
export const keepGoodsList = (params) => {
    return request({
        url: "api/keepGoods!list.action",
        method: "post",
        params
    })
};

// 收藏店铺列表
export const focusSellerList = (params) => {
    return request({
        url: "api/focusSeller!list.action",
        method: "post",
        data: params
    })
};

// 收藏商品数量
export const keepGoodsCount = () => {
    return request({
        url: "api/keepGoods!count.action",
        method: "post"
    })
};

// 收藏店铺数量
export const focusSellerCount = () => {
    return request({
        url: "api/focusSeller!count.action",
        method: "post"
    })
};
// 获取待收货代付款等数量
export const apicCuntOrderStatus = () => {
    return request({
        url: "api/order!countOrderStatus.action?",
        method: "post"
    })
};
// 获取待收货代付款等数量
export const apilogoff = (params) => {
    return request({
        url: "api/user!logoff.action",
        method: "post",
        params
    })
};
// 退出登陆
export const apiLogout = (params) => {
    return request({
        url: "api/user!logout.action",
        method: "post",
        params
    })
}

// 提现前
export const apiWithdrawBefore = (params) => {
    return request({
        url: "api/withdraw!withdraw_open.action",
        method: "post",
        params
    })
}
// 绑定地址
export const apiBindAddress = (params) => {
    return request({
        url: "api/user!bindWithdrawAddress.action",
        method: "post",
        params
    })
}
// 获取实时汇率
export const apiRealTimeExchangeRates = params => {
    return request({
        url: "api/rechargeBlockchain!fee.action",
        method: "post",
        params
    })
}
// 获取验证码
export const apiSendCode = params => {
    return request({
        url: "api/jscode!execute.action",
        method: "post",
        params
    })
}