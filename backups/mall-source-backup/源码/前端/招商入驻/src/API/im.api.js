import request from '@/request'

// 获取消息列表
export const _getMsg = (params) => {
    return request({
        url: "api/newOnlinechat!list.action",
        // loading: true,
        method: "GET",
        params: {
            message_id: params.message_id || '',  // 翻页用到
            show_img: params.show_img || true
        }
    })
};
///图片上传  /public/uploadimg!execute.action
export const tupianshangchuan_post2 = (params) => {
    return request({
        url: "api/uploadimg!execute.action",
        method: "post",
        isLoading: true,
        data: params,

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
        // loading: true,
        method: "GET",
        params: {
            type, // 消息类型， img / text
            content
        }
    })
};

