import request from './request'
import { METHODS } from '@/config'

//修改登录密码 用旧密码
export const _changePassword = (params) => {
    return request({
        url: "/wap/api/user/updateOldAndNewPsw",
        method: METHODS.POST,
        data: params
    })
};
//修改登录密码 用验证码
export const _updatepsw = (params) => {
    return request({
        url: "/wap/api/user/updatepsw",
        method: METHODS.POST,
        data: params
    })
};

//重置登录密码 用验证码 （用于忘记密码）
export const _resetpsw = (params) => {
    return request({
        url: "/wap/api/user/resetpsw",
        method: METHODS.POST,
        data: params
    })
};


//设置资金密码
export const _setSafewordReg = (params) => {
    return request({
        url: "/wap/api/user/setSafewordReg",
        method: METHODS.POST,
        data: params
    })
};
//修改资金密码 用旧密码
export const _changeFundsPassword = (params) => {
    return request({
        url: "/wap/api/user/updateOldAndNewSafeword",
        method: METHODS.POST,
        data: params
    })
};
//修改资金密码 用验证码
export const _setSafeword = (params) => {
    return request({
        url: "/wap/api/user/setSafeword",
        method: METHODS.POST,
        data: params
    })
};

//绑定邮箱
export const _bindEmail = (params) => {
    return request({
        url: "/api/user/bind-email",
        method: METHODS.POST,
        data: params
    })
};
//绑定手机
export const _bindPhone = (params) => {
    return request({
        url: "/api/user/bind-phone",
        method: METHODS.POST,
        data: params
    })
};

// 检测账号是否重复
export const checkAccount = (params) => {
    return request({
        loadingPass: true,
        url: "/wap/api/user/checkAccount",
        method: METHODS.POST,
        data: params
    })
};


// 绑定邮箱或者手机号
export const bindEmailOrPhone = (params) => {
    return request({
        url: "/wap/api/localuser/bindEmailOrPhone",
        method: METHODS.POST,
        data: params
    })
};

// 修改手机号-不收验证码
export const bindEmailOrPhoneSm = (params) => {
    return request({
        url: "/wap/api/localuser/bindEmailOrPhoneSm",
        method: METHODS.POST,
        data: params
    })
};

// 验证邮箱或者手机号
export const checkEmailOrPhone = (params) => {
    return request({
        url: "/wap/api/localuser/checkEmailOrPhone",
        method: METHODS.POST,
        data: params
    })
};

// 绑定邮箱或者手机号之前校验账号
export const beforeBindVer = (params) => {
    return request({
        url: "/wap/api/localuser/beforeBind",
        method: METHODS.POST,
        data: params
    })
};

//获取验证方式(token)
export const _getVerifTarget = (params) => {
    return request({
        url: "/wap/api/user/getVerifTarget",
        method: METHODS.POST,
        data: params
    })
};

//获取验证方式（用户名）
export const _getUserNameVerifTarget = (params) => {
    return request({
        url: "/wap/api/user/getUserNameVerifTarget",
        method: METHODS.POST,
        data: params
    })
};


//获取谷歌验证器绑定信息
export const _getGoogleauth = (params) => {
    return request({
        url: "/wap/api/googleauth/get",
        method: METHODS.POST,
        data: params
    })
};

//谷歌验证器绑定
export const _bindGoogleauth = (params) => {
    return request({
        url: "/wap/api/googleauth/bind",
        method: METHODS.POST,
        data: params
    })
};

//获取人工重置信息
export const _getSafewordApply = (params) => {
    return request({
        url: "/api/user/safeword/apply/list",

        method: METHODS.POST,
        data: params
    })
};
//人工重置申请
export const _setSafewordApply = (params) => {
    return request({
        url: "/api/user/safeword/apply",
        method: METHODS.POST,
        data: params
    })
};


//高级认证申请
export const _kycHighLevelApply = (params) => {
    return request({
        url: "/wap/api/kycHighLevel/apply",
        method: METHODS.POST,
        data: params
    })
};
//高级认证信息
export const _getKycHighLevel = (params) => {
    return request({
        url: "/wap/api/kycHighLevel/get",
        method: METHODS.POST,
        data: params
    })
};

//轮播
export const _getBanner = (params) => {
    return request({
        url: "/wap/api/banner/list",
        method: METHODS.POST,
        data: params
    })
};

//服务条款
export const _getCms = (params) => {
    return request({
        url: "/api/cms/",
        method: METHODS.POST,
        data: params
    })
};


//获取新闻列表
export const _getNewsList = (params) => {
    return request({
        url: "/api/news/list",
        method: METHODS.POST,
        data: params,
    })
};

//获取新闻
export const _getNews = (params) => {
    return request({
        url: "/wap/api/news/get",
        method: METHODS.POST,
        data: params,
    })
};

//获取用户信息
export const _info = (params) => {
    return request({
        url: "/wap/api/localuser/get",
        method: "GET",
        data: params,
    })
}

// 获取余额
export const _getBalance = () => {
    return request({
        url: "/wap/api/wallet/getUsdt",
        method: "GET",
    })
};

// 申请认证
export const _applyIdentify = (data, flag) => {
    const params = {
        nationality: data.nationality, // 国籍
        idname: data.idname || '身份证', // 证件名称
        idnumber: data.idnumber, // 证件号码
        name: data.name, // 姓名
        idimg_1: data.frontFile.length ? data.frontFile[0].resURL || data.frontFile[0].url : '',
        idimg_2: data.reverseFile.length ? data.reverseFile[0].resURL || data.reverseFile[0].url : '',
        idimg_3: data.fileList.length ? data.fileList[0].resURL || data.fileList[0].url : ''
    }
    if (flag) {
        delete params.idimg_3
    }
    return request({
        url: '/wap/api/kyc/apply',
        method: 'GET',
        loadingPass: false,
        params
    })
}

// 认证信息
export const _getIdentify = () => {
    return request({
        url: '/wap/api/kyc/get',
        method: 'POST'
    })
}

export const messagePagelist = (data) => {
    return request({
        url: '/wap/api/notification/message.pagelist',
        method: 'GET',
        params: data
    })
}

export const messageSlidelist = (data) => {
    return request({
        url: '/wap/api/notification/message.slidelist',
        method: 'GET',
        params: data
    })
}

export const messageDetail = (data) => {
    return request({
        url: '/wap/api/notification/message.detail',
        method: 'GET',
        params: data
    })
}

export const messageRead = (data) => {
    return request({
        url: '/wap/api/notification/message.read',
        method: 'POST',
        data
    })
}

export const countUnread = (data) => {
    return request({
        url: '/wap/api/notification/count.unread',
        method: 'GET',
        params: data
    })
}

export const unreadCount = (data) => {
    return request({
        url: '/wap/public/userOnlineChatController/unread',
        method: 'GET',
        loadingPass: true,
        params: data
    })
}

export const chatUserlist = (data) => {
    return request({
        url: '/wap/public/userOnlineChatController/userlist',
        method: 'GET',
        params: data
    })
}

export const refreshAvatar = (data) => {
    return request({
        url: '/wap/api/localuser/refreshAvatar',
        method: 'POST',
        loadingPass: true,
        data
    })
}

// 国家数据
export const listCountry = (data) => {
    return request({
        url: '/wap/api/address/listCountry',
        method: 'POST',
        loadingPass: true,
        data
    })
}

export const firstRechargeRewargs = () => {
    return request({
        url: '/wap/api/syspara/getSyspara?code=mall_first_recharge_rewards',
        method: 'GET',
    })
}

// 客服跳转链接
export const customerServiceUrl = () => {
    return request({
        url: '/wap/api/syspara/getSyspara?code=customer_service_url',
        loadingPass: true,
        method: 'GET',
    })
}

// 配置参数
export const getSysparaAction = (type) => {
    return request({
        url: `/wap/api/syspara/getSyspara?code=${type}`,
        method: 'GET',
    })
}

// 领取邀请好友奖励
export const receiveInviteRewards = () => {
    return request({
        url: `/wap/seller/seller/receiveInviteRewards`,
        method: 'POST',
        loadingPass: true,
    })
}

export const beforeReceiveBonus = () => {
    return request({
        url: "/wap/seller/seller/beforeReceiveBonus",
        method: METHODS.POST
    })
}

export const receiveBonus = (data) => {
    return request({
        url: "/wap/seller/seller/receiveBonus",
        method: METHODS.POST,
        data
    })
}

export const userLogOff = (data) => {
    return request({
        url: "/wap/api/user/logoff",
        method: METHODS.POST,
        data
    })
}

// 变账加钱通知
export const moneylogAddNotify = () => {
    return request({
        url: `/wap/api/moneylog/addNotify`,
        method: 'GET',
        loadingPass: true,
    })
}

// 变账加钱通知已读
export const moneylogNotifyCallback = (data) => {
    return request({
        url: `/wap/api/moneylog/notifyCallback`,
        method: METHODS.POST,
        data
    })
}