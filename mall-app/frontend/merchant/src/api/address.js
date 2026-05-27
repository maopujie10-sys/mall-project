import request from '@/utils/request'

export function listCountry(query) {//查询国家
    return request({
        url: '/api/address!listCountry.action',
        method: 'post',
        isLoading: true,
        params: query
    })
}

export function listState(query) {//查询省
    return request({
        url: '/api/address!listState.action',
        method: 'post',
        isLoading: true,
        params: query
    })
}

export function listCity(query) {//查询城市
    return request({
        url: '/api/address!listCity.action',
        method: 'post',
        isLoading: true,
        params: query
    })
}


