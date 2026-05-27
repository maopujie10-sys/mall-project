import request from '@/utils/request'

export function getCategory(params) {
    return request({
        url: 'api/category!list.action',
        method: "post",
        isLoading: true,
        params
    })
}
