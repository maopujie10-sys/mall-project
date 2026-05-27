import request from '@/utils/request'

export function searchUser(name) {
    return request({
        url: '/vue-element-admin/search/user',
        method: 'get',
        isLoading: true,
        params: {name}
    })
}

export function transactionList(query) {
    return request({
        url: '/vue-element-admin/transaction/list',
        method: 'get',
        isLoading: true,
        params: query
    })
}
