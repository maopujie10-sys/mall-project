import request from '@/utils/request'
import axios from "axios";
// import {compress, compressAccurately} from 'image-conversion';
// import Config from "@/config";
// import { Toast } from "vant";
import Toast from "@/utils/toast";
import {getOrigin} from '@/utils/utis'

const BASE_URL = process.env.NODE_ENV === 'production' ? '' : ''

// 图片上传
export const _uploadImage = (file, callback) => {
    const isLt2M = file.file.size / 1024 / 1024 < 10;
    if (!isLt2M) {
        Toast.fail('上传头像图片大小不能超过 10MB!');
        return false;
    }
    // Toast.loading()
    return new Promise((resolve, reject) => {
        compress(file.file, 0.6).then(res => {
            const formData = new FormData()
            formData.append('file', res)
            axios.post(`${getOrigin()}/wap/api/uploadimg!execute.action`,
                formData,
                {
                    onDownloadProgress: (progressEvent) => {
                        console.log(progressEvent)
                        if (progressEvent.lengthComputeable) {
                            callback(((progressEvent.loaded / progressEvent.total) * 100).toFloor(2))
                        }
                    }
                },
                {
                    headers:
                        {"Content-Type": "multipart/form-data"}
                }).then(res => {
                // Toast.clear()
                const {code, data} = res.data
                if (code / 1 === 0) {
                    resolve(data)
                }
            }).catch(err => {
                // Toast.clear()
                reject(err)
            })
        })
    })
}

// 申请认证
export const _applyIdentify = data => {
    return request({
        url: '/api/kyc!apply.action',
        method: 'GET',
        loading: true,
        duration: 0,
        params: {
            nationality: data.countryName, // 国籍
            idname: data.idname || 'id/passpost', // 证件名称
            idnumber: data.idnumber, // 证件号码
            name: data.name, // 姓名
            idimg_1: data.frontFile.length && data.frontFile[0].resURL || '',
            idimg_2: data.reverseFile.length && data.reverseFile[0].resURL || '',
            idimg_3: data.fileList.length && data.fileList[0].resURL || ''
        }
    })
}

// 认证信息
export const _getIdentify = (params) => {
    return request({
        url: '/api/kyc!get.action',
        method: 'GET',
        params: params,
        isLoading: false,
    })
}

// =================   兑换 ================


export const _getWallet = () => {
    return request({
        url: '/api/wallet!get.action',
        isLoading: true,
        method: 'GET'
    })
}

// 初始化接口
export const _initExchange = () => {
    return request({
        url: '/api/exchangeapplyorder!view.action',
        isLoading: true,
        method: 'GET'
    })
}

// 兑换
export const _exchange = (params) => {
    return request({
        url: '/api/exchangeapplyorder!buy_and_sell.action',
        method: 'GET',
        isLoading: true,
        params: {
            volume: params.volume, // 数量
            symbol: params.symbol.toLowerCase(), // 兑换币
            symbol_to: params.symbol_to.toLowerCase(), // 兑换后的币
            session_token: params.session_token //
        }
    })
}

// 汇率
export const _exchangeRage = (params) => {
    return request({
        url: '/api/exchangeapplyorder!buy_and_sell_fee.action',
        method: 'GET',
        isLoading: true,
        params: {
            symbol: params.symbol.toLowerCase(), // 兑换币
            symbol_to: params.symbol_to.toLowerCase(), // 兑换后的币
            volume: params.volume || 1 // 兑换数量
        }
    })
}

// 兑换历史
export const _exchangeHistory = page_no => {
    return request({
        url: '/api/exchangeapplyorder!list.action',
        method: 'GET',
        isLoading: true,
        params: {
            page_no
        }
    })
}

// 获取质押余额
export const _getBalance = () => {
    return request({
        url: '/api/dapp!getbalance.action',
        isLoading: true,
        method: "GET"
    })
}

// 提现初始化参数
export const _initWidthdrawl = (eth) => {
    return request({
        url: '/api/dapp!exchange_fee.action',
        method: "GET",
        isLoading: true,
        params: {
            eth
        }
    })
}

// 提现申请
export const _widthdrawl = (eth) => {
    return request({
        url: '/api/dapp!exchange.action',
        method: "GET",
        isLoading: true,
        params: {
            eth
        }
    })
}

// 交易记录
export const _records = (action = 'exchange', page_no = 1) => { // transfer
    return request({
        url: '/api/dapp!logs.action',
        method: "GET",
        isLoading: true,
        params: {
            action,
            page_no
        }
    })
}


// 充值详情
export const _rechargeDetail = (order_no) => {
    return request({
        url: "api/rechargeBlockchain!get.action",
        method: "get",
        isLoading: true,
        params: {
            order_no
        }
    })
}

// 提现详情
export const _withdrawDetail = (order_no) => {
    return request({
        url: "api/withdraw!get.action",
        method: "get",
        isLoading: true,
        params: {
            order_no
        }
    })
}

// 帐变记录
export const _fundRecord = (category = 'exchange', page_no = 1) => {
    return request({
        url: "api/moneylog!list.action",
        method: "get",
        isLoading: true,
        params: {
            category,
            page_no
        }
    })
}
