import Axios from '@/util/http'
import axios from "axios";
import {compress} from 'image-conversion';

// 获取消息列表
export const _getMsg = (message_id= '', show_img = true) => {
    return new Promise((resolve, reject) => {
        Axios.fetch('api/newOnlinechat!list.action', {message_id,show_img }).then(res => {
            resolve(res.data)
        })
    }) 
    
    // return request({
    //     url: "api/newOnlinechat!list.action",
    //     // loading: true,
    //     method: "GET",
    //     params: {
    //         message_id: params.message_id || '',  // 翻页用到
    //         show_img: params.show_img || true
    //     }
    // })
};

// 未读消息
export const _getUnreadMsg = () => {
    return Axios.fetch('api/newOnlinechat!unread.action', params)
    // return request({
    //     url: "api/newOnlinechat!unread.action",
    //     loading: true,
    //     method: "GET",
    // })
};

// 发送消息
export const _sendMsg= (type = 'text', content = '') => {
    return Axios.fetch('/api/newOnlinechat!send.action', {type, content})
    // return request({
    //     url: "api/newOnlinechat!send.action",
    //     // loading: true,
    //     method: "GET",
    //     params: {
    //         type, // 消息类型， img / text
    //         content
    //     }
    // })
};

// 图片上传
export const _uploadImage = (file, callback) => {
    console.log(file)
    const isLt2M = file.size / 1024 / 1024 < 10;
    if (!isLt2M) {
        Toast.fail('上传头像图片大小不能超过 10MB!');
        return false;
    }
    // Toast.loading()
    // const BASE_URL = 'https://' + window.location.hostname
    const BASE_URL = ''
    return new Promise((resolve, reject) => {
        compress(file, 0.6).then(res => {
            const formData = new FormData()
            formData.append('file', res)
            axios.post(`${BASE_URL}public/uploadimg!execute.action`,
                formData,
                {
                    onDownloadProgress: (progressEvent) => {
                        console.log(progressEvent)
                        if (progressEvent.lengthComputeable) {
                            callback(((progressEvent.loaded / progressEvent.total) * 100).toFixed(2))
                        }
                    }
                },
                { headers:
                    { "Content-Type": "multipart/form-data" }
                }).then(res => {
                    // Toast.clear()
                    const { code, data } =res.data
                    if (code / 1=== 0) {
                        resolve(data)
                    }
                }).catch(err => {
                    // Toast.clear()
                    reject(err)
                })
            })
        })
    }