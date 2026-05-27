import request from '@/utils/request'

// 获取消息列表
export const _getMsg = (params) => {
    return request({
        url: "api/newOnlinechat!list.action",
        method: "GET",
        params: {
            message_id: params.message_id || '',  // 翻页用到
            show_img: params.show_img || true
        }
    })
};

// 未读消息
export const _getUnreadMsg = () => {
    return request({
        url: "api/newOnlinechat!unread.action",
        loading: true,
        method: "GET",
    })
};

// 发送消息
export const _sendMsg = (type = 'text', content = '') => {
    return request({
        url: "api/newOnlinechat!send.action",
        method: "GET",
        params: {
            type, // 消息类型， img / text
            content
        }
    })
};


// 站内信列表 PC端分页查看消息记录
export const getMessage = (params) => {
    return request({
        url: "api/notification!message.pagelist",
        isLoading: false,
        method: "GET",
        params
    })
};

// 站内信未读数量
export const getMessageNumber = (params) => {
    return request({
        url: "api/notification!count.unread",
        isLoading: false,
        method: "GET",
        params
    })
}
// 站内信 变成已读
export const readMessage = (params) => {
    return request({
        url: "api/notification!message.read",
        isLoading: false,
        method: "POST",
        params
    })
}

//获取未处理的订单总数
export const getUnprocessedOrder = (params) => {
    return request({
        url: "seller/orders!noPushNum.action",
        isLoading: false,
        method: "post",
        params
    })
}
