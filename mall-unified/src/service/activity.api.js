import request from './request'
import {METHODS} from '@/config'

/**
 * 抽奖活动详情
 */
export const lotteryInfo = (data) => request({
    url: '/api/activity/lottery/detail',
    method: METHODS.GET,
    params: data
})

/**
 * 查询用户积分
 */
export const getPoints = (data) => request({
    url: '/api/activity/lottery/points',
    method: METHODS.GET,
    params: data
})

/**
 * 抽奖
 */
export const lotteryDraw = (data) => request({
    url: '/api/activity/lottery/draw',
    method: METHODS.POST,
    params: data
})

/**
 * 中奖统计
 */
export const lotteryCountPrize = (data) => request({
    url: '/api/activity/lottery/count-prize',
    method: METHODS.GET,
    params: data
})

/**
 * 中奖统计
 */
export const receivePrize = (data) => request({
    url: '/api/activity/lottery/receive-prize',
    method: METHODS.POST,
    params: data
})

/**
 * 查询邀请累计人数以及积分
 */
export const getCountPoints = (data) => request({
    url: '/api/activity/lottery/count-points',
    method: METHODS.POST,
    params: data
})

/**
 * 我的中奖列表
 */
export const pageListMyPrize = (data) => request({
    url: '/api/activity/lottery/my-prizes',
    method: METHODS.GET,
    params: data
})

/**
 * 查询展示活动
 */
export const getCurrentActivity = () => request({
    url: '/api/activity/lottery/current',
    method: METHODS.GET
})
