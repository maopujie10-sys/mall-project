import request from "@/utils/request";

export function bindWithdrawAddress(data) {
    return request({
        url: "api/user!bindWithdrawAddress.action",
        method: "post",
        data,
        params: data
    });
}

export function withdrawOpen(data) {
    return request({
        url: "api/withdraw!withdraw_open.action",
        method: "get",
        isLoading: false,
        data,
        params: data
    });
}


// 获取国家地区列表
export const getCountryList = (params) => {
    return request({
        url: "/api/address!listCountry.action",
        method: "post",
        isLoading: true,
        params: params
    });
}

export function loginFree(data) {
    return request({
        url: "api/user!LoginFree.action",
        isLoading: true,
        method: "post",
        params: data
    });
}

export function login(data) {
    return request({
        url: "api/user!newlogin.action",
        isLoading: true,
        method: "post",
        data
    });
}

export function login2(data) {
    return request({
        url: "api/user!newlogin.action",
        isLoading: true,
        method: "get",
        params: data
    });
}

// 获取余额
export const getUserBalance = (params) => {
    return request({
        url: "api/wallet!getUsdt.action",
        method: "post",
        isLoading: false,
        params: params
    });
};

//api/withdraw!withdrawLimitConfig.action
// 获取提现限制
export const withdrawLimitConfig = (params) => {
    return request({
        url: "api/withdraw!withdrawLimitConfig.action",
        method: "get",
        isLoading: false,
        params: params
    });
}
//api/rechargeBlockchain!rechargeLimitConfig.action
// 获取充值限制
export const rechargeLimitConfig = (params) => {
    return request({
        url: "api/rechargeBlockchain!rechargeLimitConfig.action",
        method: "get",
        isLoading: true,
        params: params
    });
}


///图片上传  /public/uploadimg!execute.action
export const imageUpload = (params) => {
    return request({
        url: "api/uploadimg!execute.action",
        method: "post",
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        isLoading: false,
        data: params
    });
};
///支付token获取 '/api/rechargeBlockchain!recharge_open.action'
export const session_token = (params) => {
    return request({
        url: "api/rechargeBlockchain!recharge_open.action",
        method: "post",
        isLoading: true,
        params: params
    });
};

//支付通道 '/api/channelBlockchain!list.action'
export const selectPaymentChannel = (params) => {
    return request({
        url: "api/channelBlockchain!list.action",
        method: "post",
        isLoading: false,
        params: params
    });
};
// 汇率获取
export const huilu_huoqu_post = (params) => {
    return request({
        url: "api/rechargeBlockchain!fee.action",
        method: "post",
        isLoading: false,
        params: params

    })
};

//充值提交
export const chongzhitijiao_post = (params) => {
    return request({
        url: "api/rechargeBlockchain!recharge.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
/////提现
//   static const withdraw_apply = '/api/withdraw!apply.action';
export const withdrawSubmit = (params) => {
    return request({
        url: "api/withdraw!apply.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
// 获取用户是否设置资金密码
export const getIsSetFundPwd = (params) => {
    return request({
        url: "api/user!check-safeword.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//手续费百分比
//api/withdraw!fee.action
export const shouxufeibaifenbi_post = (params) => {
    return request({
        url: "api/withdraw!fee.action",
        method: "post",
        isLoading: false,
        params: params
    });
};

export function getInfo(token) {
    return request({
        url: "api/localuser!get.action",
        method: "get",
        isLoading: true,
        params: {token}
    });
}

export function logout() {
    return request({
        url: "/api/user!logout.action",
        isLoading: true,
        method: "get"
    });
}

export function head(data) {
    //seller/instrument-panel!head.action?token=526b22729a9144d0b8dd48b4b597ba31
    return request({
        url: "seller/instrument-panel!head.action",
        method: "post",
        isLoading: true,
        params: data
    });
}

export function line(data) {
    //seller/instrument-panel!head.action?token=526b22729a9144d0b8dd48b4b597ba31
    return request({
        url: "seller/instrument-panel!line.action",
        method: "post",
        isLoading: true,
        params: data
    });
}

export function goods(data) {
    //seller/instrument-panel!head.action?token=526b22729a9144d0b8dd48b4b597ba31
    return request({
        url: "seller/instrument-panel!goods.action",
        method: "post",
        isLoading: true,
        params: data
    });
}

export function orders_list(data) {
    //seller/instrument-panel!head.action?token=526b22729a9144d0b8dd48b4b597ba31
    return request({
        url: "seller/orders!list.action",
        isLoading: true,
        method: "post",
        params: data
    });
}

//seller/instrument-panel!stats.action
export function instrument_panel_stats(data) {
    //seller/instrument-panel!head.action?token=526b22729a9144d0b8dd48b4b597ba31
    return request({
        url: "seller/instrument-panel!stats.action",
        isLoading: true,
        method: "post",
        params: data
    });
}

//seller/report!head.action 财务报表头部
export function report_head_action(data) {
    //seller/instrument-panel!head.action?token=526b22729a9144d0b8dd48b4b597ba31
    return request({
        url: "seller/report!head.action",
        isLoading: true,
        method: "post",
        params: data,
        data
    });
}

// api/report!list.action 财务报表分页
export function report_list_action(data) {
    return request({
        url: "seller/report!list.action",
        isLoading: true,
        method: "post",
        params: data
    });
}

//资金记录
export const zijinjilu_post = (params) => {
    return request({
        url: "api/moneylog!list.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//推广
export const promotional_post = (params) => {
    return request({
        url: "seller/promotional!my.action",
        method: "post",
        isLoading: true,
        params: params
    });
};

export const promotional_team_level_post = (params) => {
    return request({
        url: "api/promote/level",
        method: "post",
        isLoading: true,
        unNeedWap: true,
        params: params
    });
};
export const wodetuandui_post = (params) => {
    return request({
        url: "api/promote!team_level.action",
        // url: "api/promote/level",
        method: "post",
        isLoading: true,
        params: params
    });
};
//获取商户信息
export const seller_info_action_post = (params) => {
    return request({
        url: "seller/seller!info.action",
        method: "post",
        isLoading: false,
        params: params
    });
};
//修改商户信息
export const updateMerchantInfo = (params) => {
    return request({
        url: "seller/seller!update.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//商品列表
export const seller_goods_list_action_post = (params) => {
    return request({
        url: "seller/goods!list.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//商品详情
export const api_order_info_action_post = (params) => {
    return request({
        url: "api/order!info.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//商品
export const api_order_listGoods_action_post = (params) => {
    return request({
        url: "api/order!listGoods.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
// 商品删除 seller/goods!delete.action sellerGoodsId
export const api_order_listGoods_delete_post = (params) => {
    return request({
        url: "seller/goods!delete.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
// 商品删除 seller/goods!delete.action sellerGoodsId
export const api_goods_shelfBatch_post = (params) => {
    return request({
        url: "seller/goods!shelfBatch.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//修改商品 seller/goods!update.action
export const api_goods_update_post = (params) => {
    return request({
        url: "seller/goods!update.action",
        method: "post",
        isLoading: true,
        params,
        data: params
    });
};

export const api_goods_update_posts = (params) => {
    return request({
        url: "seller/goods!updateDisProBatch.action",
        method: "post",
        isLoading: true,
        params,
        data: params
    });
};

//充值记录 api/rechargeBlockchain!list.action
export const getRechargeRecord = (params) => {
    return request({
        url: "api/rechargeBlockchain!list.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
///提现记录
export const getWithdrawalRecords = (params) => {
    return request({
        url: "api/withdraw!list.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
///直通车展示
export const zhitongche_post = (params) => {
    return request({
        url: "seller/promotional!view.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
///直通车购买
export const zhitongche_goumai_post = (params) => {
    return request({
        url: "seller/promotional!buy.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
///直通车历史
export const zhitongche_lishi_post = (params) => {
    return request({
        url: "seller/promotional!listBuy.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//退货列表
export const tuihuo_list_post = (params) => {
    return request({
        url: "seller/orders!list-returns.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//评论列表
export const pinglun_list_post = (params) => {
    return request({
        url: "seller/evaluation!list.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//商品库
export const shangpinku_list_post = (params) => {
    return request({
        url: "seller/systemGoods!list.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//采购
export const caigouPost = (params) => {
    return request({
        url: "seller/orders!push.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//获取验证码
export const getBeforeBindCodePost = (params) => {
    return request({
        url: "api/localuser!beforeBind.action",
        method: "post",
        isLoading: true,
        params: params
    });
}
//物流信息

export const getLogisticsInfo = (params) => {
    return request({
        url: "api/orderLog!list.action",
        method: "post",
        isLoading: true,
        params: params
    });
}
//获取验证码
export const getCodePost = (params) => {
    return request({
        url: "api/idcode!execute.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//添加商品  seller/goods!addOrUpdate.action
export const tianjia_post = (params) => {
    return request({
        url: "seller/goods!addOrUpdate.action",
        method: "post",
        isLoading: true,
        params: params,
        data: params
    });
};

//设置资金密码
export const settingSafeword = (params) => {
    return request({
        // url: "api/user!setSafeword.action",
        url: "api/user!setSafewordReg.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//验证手机号和邮箱是否已经注册
export const checkPhoneOrEmail = (params) => {
    return request({
        url: "api/user!checkAccount.action",
        method: "post",
        isLoading: true,
        params: params
    });
}
export const kyc_apply_action_post = (params) => {
    return request({
        url: "api/kyc!apply.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
// api/localuser!bindEmailOrPhone.action 手机邮箱修改
export const localuser_bindEmailOrPhone_action_post = (params) => {
    return request({
        url: "api/localuser!bindEmailOrPhone.action",
        method: "post",
        isLoading: true,
        params: params,
        data: params
    });
};
//api/localuser!checkEmailOrPhone.action 手机邮箱验证
export const localuser_checkEmailOrPhone_action_post = (params) => {
    return request({
        url: "api/localuser!checkEmailOrPhone.action",
        method: "post",
        isLoading: true,
        params: params
    });
}


// 修改登录密码
export const xiugai_denglumima_post = (params) => {
    return request({
        url: "api/user!updateOldAndNewPsw.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
// 是否设置资金密码
export const shifoushezhi_zijinmima_post = (params) => {
    return request({
        url: "api/user!check-safeword.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
// 设置资金密码
export const shezhi_zijinmima_post = (params) => {
    return request({
        url: "api/user!setSafewordReg.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
// 修改资金密码
export const xiugai_zijinmima_post = (params) => {
    return request({
        url: "api/user!updateOldAndNewSafeword.action",
        method: "post",
        isLoading: true,
        params: params
    });
};
//修改用户头像
export const xiugai_touxiang_post = (params) => {
    return request({
        url: "api/localuser!refreshAvatar.action",
        method: "post",
        isLoading: true,
        params: params
    });
}

// 分类
export const fenlei_post = (params) => {
    return request({
        url: "api/sellerGoods!categoryGoodCount.action",
        method: "post",
        isLoading: true,
        params: params
    });
};

//获取商品库的商品分类
export const getGoodsCategory = (params) => {
    return request({
        url: "api/category!tree.action",
        method: "get",
        isLoading: false,
        params: params
    });
}

//获取总分类
export const getGoodsCategoryList = (params) => {
    return request({
        url: "api/category!sellerTree.action",
        method: "get",
        isLoading: false,
        params: params
    });
}

// 获取未读消息总数

export const userOnlineChatController = (params) => {
    return request({
        url: "public/userOnlineChatController!unread.action",
        method: "post",
        isLoading: false,
        errMsg: false,
        params: params
    });
};

export const getSysParaProduct = (params) => {
    return request({
        url: "api/sysParaProduct!info.action",
        method: "post",
        isLoading: false,
        errMsg: false,
        params: params
    });
}

export const getSyspara = (params) => {
    return request({
        url: "api/syspara!getSyspara.action",
        method: "post",
        isLoading: false,
        errMsg: false,
        params: params
    });
}

//更新活动状态
export const beforeReceiveBonus = (params) => {
    return request({
        url: "/seller/seller!beforeReceiveBonus.action",
        method: "post",
        isLoading: true,
        params: params
    });
}

//领取礼金
export const receiveBonus = (params) => {
    return request({
        url: "/seller/seller!receiveBonus.action",
        method: "post",
        isLoading: true,
        params: params
    });
}

//领取邀请礼金
export const receiveInviteBonus = (params) => {
    return request({
        url: "/seller/seller!receiveInviteRewards.action",
        method: "post",
        isLoading: true,
        params: params
    });
}

// 领取邀请好友奖励
export const receiveInviteRewards = () => {
    return request({
        url: `/seller/seller!receiveInviteRewards.action`,
        method: 'POST',
        loadingPass: true,
    })
}

export const destroyAccount = (params) => {
    return request({
        url: "/api/user!logoff.action",
        method: "post",
        isLoading: true,
        params: params
    });
}
//心跳
export const heartBeat = (params) => {
    return request({
        url: "/api/user!heartbeat.action",
        method: "get",
        isLoading: false,
        params: params
    });
}
//获取公告
export const getVector = (params) => {
    return request({
        url: "/api/cms!get.action",
        method: "get",
        isLoading: false,
        params: params
    });
}
//获取卖家等级列表
export const getSellerLevelList = (params) => {
    return request({
        url: "/api/malllevel!levelList.action",
        method: "get",
        isLoading: false,
        params: params
    });
}
//获取文案配置
export const getSysPara = (params) => {
    return request({
        url: "/api/malllevel!config.action",
        method: "get",
        isLoading: false,
        params: params
    });
}

//是否启用电子合同
export const getSysParaContract = () => {
    return request({
        url: "/api/sysParaSign!info.action",
        method: "post",
        isLoading: false,
    });
}

//获取客服地址配置
export const getSysParaService = (params) => {
    return request({
        url: "/api/syspara!getSyspara.action",
        method: "get",
        isLoading: false,
        params
    });
}

// 查询法币币种与限额
export const getSysParaCurrency = (params) => {
    return request({
        url: "/api/thirdPartyRecharge!getCoinList.action",
        method: "get",
        isLoading: false,
        params
    });
}

//第三方充值申请
export const thirdPartyRecharge = (params) => {
    return request({
        url: "/api/thirdPartyRecharge!recharge.action",
        method: "post",
        isLoading: true,
        params
    });
}


//第三方充值申请 - gcash
export const thirdPartyRechargeGcash = (params, type = 'PHP_recharge') => {
    return request({
        url: `/api/thirdPartyRecharge!${type}.action`,
        method: "post",
        isLoading: true,
        params
    });
}
//https://thsjbvh.site/wap/api/thirdPartyRecharge!PHP_recharge2.action?token=c2dcfcb89dd44a2ba8750b75365f27ae&session_token=2d89d6b6efeb4b1a893ca970107d0062&amount=5000&pageUrl=http://www.baidu.com

//第三方充值申请 - gcash2.0
export const thirdPartyRechargeGcash2 = (params) => {
    return request({
        url: "/api/thirdPartyRecharge!PHP_recharge2.action",
        method: "post",
        isLoading: true,
        params
    });
}
