import request from '@/utils/request'

export function fetchList(query) {
    return request({
        url: '/vue-element-admin/article/list',
        method: 'get', isLoading: true,
        params: query
    })
}

export function fetchArticle(id) {
    return request({
        url: '/vue-element-admin/article/detail',
        method: 'get', isLoading: true,
        params: {id}
    })
}

export function fetchPv(pv) {
    return request({
        url: '/vue-element-admin/article/pv',
        method: 'get', isLoading: true,
        params: {pv}
    })
}

export function createArticle(data) {
    return request({
        url: '/vue-element-admin/article/create',
        method: 'post', isLoading: true,
        data
    })
}

export function updateArticle(data) {
    return request({
        url: '/vue-element-admin/article/update',
        method: 'post', isLoading: true,
        data
    })
}
