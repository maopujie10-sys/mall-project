import request from './request'
import {METHODS} from '@/config'

/**
 * 抽奖活动详情
 */
export const lotteryInfo = (data) => request({
    url: '/wap/api/activity/lottery!detail.action',
    method: METHODS.GET,
    params: data
})

/**
 * 查询用户积分
 */
export const getPoints = (data) => request({
    url: '/wap/api/activity/lottery!getPoints.action',
    method: METHODS.GET,
    params: data
})

/**
 * 抽奖
 */
export const lotteryDraw = (data) => request({
    url: '/wap/api/activity/lottery!draw.action',
    method: METHODS.POST,
    params: data
})

/**
 * 中奖统计
 */
export const lotteryCountPrize = (data) => request({
    url: '/wap/api/activity/lottery!countPrize.action',
    method: METHODS.GET,
    params: data
})

/**
 * 中奖统计
 */
export const receivePrize = (data) => request({
    url: '/wap/api/activity/lottery!receivePrize.action',
    method: METHODS.POST,
    params: data
})

/**
 * 查询邀请累计人数以及积分
 */
export const getCountPoints = (data) => request({
    url: '/wap/api/activity/lottery!getCountPoints.action',
    method: METHODS.POST,
    params: data
})

/**
 * 我的中奖列表
 */
export const pageListMyPrize = (data) => request({
    url: '/wap/api/activity/lottery!pageListMyPrize.action',
    method: METHODS.GET,
    params: data
})

/**
 * 查询展示活动
 */
export const getCurrentActivity = () => request({
    url: '/wap/api/activity/lottery!getCurrentActivity.action',
    method: METHODS.GET
})
