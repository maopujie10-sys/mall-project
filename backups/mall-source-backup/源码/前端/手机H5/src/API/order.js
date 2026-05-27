import request from "@/request";

// 物流信息
export const getLogisticsInformation = (params) => {
    return request({
        url: "api/orderLog!list.action",
        method: "get",
        params
    })
};
