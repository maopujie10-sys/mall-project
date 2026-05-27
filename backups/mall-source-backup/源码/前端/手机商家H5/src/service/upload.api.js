// 图片上传
import axios from "axios";
import { Toast } from "vant";
import { IMG_PATH } from '@/config'
import { compress } from 'image-conversion';
import { useUserStore } from "@/store/user.js";
import request from './request'
import {METHODS} from "../config/index.js";

export const _uploadImage = (file, callback) => {
    const isLt2M = file.file.size / 1024 / 1024 < 10;
    if (!isLt2M) {
        Toast.fail('上传图片大小不能超过 10MB!');
        return false;
    }
    const userStore = useUserStore()
    const TOKEN = userStore?.userInfo?.token
    return new Promise((resolve, reject) => {
        compress(file.file, 0.6).then(res => {
            const formData = new FormData()
            formData.append('file', res)
            console.log(IMG_PATH)
            axios.post(`${IMG_PATH}/wap/public/uploadimg!execute.action?token=${TOKEN}`,
                formData,
                {
                    onDownloadProgress: (progressEvent) => {
                        console.log(progressEvent)
                        if (progressEvent.lengthComputeable) {
                            callback(((progressEvent.loaded / progressEvent.total) * 100).toFixed(2))
                        }
                    }
                },
                {
                    headers:
                        { "Content-Type": "multipart/form-data" },
                    timeout: 5000,
                }).then(res => {
                    const { code, data } = res.data
                    if (code / 1 === 0) {
                        resolve(data)
                    }
                }).catch(err => {
                    reject(err)
                })
        })
    })
}


export const uploadimgExecute = (data) => {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('moduleName', data.moduleName)
    return request({
        url: "/wap/api/uploadimg!execute.action",
        method: METHODS.POST,
        data: formData
    })
}
