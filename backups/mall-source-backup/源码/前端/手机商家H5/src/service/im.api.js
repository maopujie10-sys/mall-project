import request from './request'

// 获取消息列表
export const _getMsg = (params) => {
    return request({
        url: "/wap/api/newOnlinechat!list.action",
        // loading: true,
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
        url: "/wap/api/newOnlinechat!unread.action",
        // loading: true,
        method: "GET",
    })
};

// 发送消息
export const _sendMsg = (type = 'text', content = '') => {
    return request({
        url: "/wap/api/newOnlinechat!send.action",
        // loading: true,
        method: "GET",
        params: {
            type, // 消息类型， img / text
            content
        }
    })
};