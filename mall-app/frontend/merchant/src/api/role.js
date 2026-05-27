import request from '@/utils/request'

export function getRoutes() {
    return request({
        url: '/vue-element-admin/routes',
        isLoading: true,
        method: 'get'
    })
}

export function getRoles() {
    return request({
        url: '/vue-element-admin/roles',
        isLoading: true,
        method: 'post',
    })
}

export function addRole(data) {
    return request({
        url: '/vue-element-admin/role',
        method: 'post',
        isLoading: true,
        data
    })
}

export function updateRole(id, data) {
    return request({
        url: `/vue-element-admin/role/${id}`,
        method: 'put',
        isLoading: true,
        data
    })
}

export function deleteRole(id) {
    return request({
        url: `/vue-element-admin/role/${id}`,
        isLoading: true,
        method: 'delete'
    })
}
