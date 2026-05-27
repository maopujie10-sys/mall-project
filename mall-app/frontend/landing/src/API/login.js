import request from "@/request";

const getCurrentProjectInfo = (params) => {
    return request({
        url: "projectInfoApp/getCurrentProjectInfo",
        method: "get",
        isLoading: true
    }, params)
};
const zhanghaodenglu = (params) => {
    return request({
        url: "api/user!login.action",
        method: "post",
        isLoading: true,
        params:params
    })
};
const zhanghaozhuce = (params) => {
    return request({
        url: "api/localuser!register_username.action",
        method: "post",
        isLoading: true,
        params:params
    })
};
const shoujihaozhuce = (params) => {
    return request({
        url: "api/localuser!register.action",
        method: "get",
        isLoading: true,
        params:params
    })
};
const shoujihaodenglu = (params) => {
    return request({
        url: "api/user!login_idcode.action",
        method: "post",
        isLoading: true,
        params:params
    })
};
const apiList = {
    getCurrentProjectInfo,
    zhanghaodenglu,
    zhanghaozhuce,
    shoujihaozhuce,
    shoujihaodenglu
}

export default apiList
