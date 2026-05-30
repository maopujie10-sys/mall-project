import request from './request'
import {METHODS} from "../config/index.js";

export const sellerReportHead = (data) => {
    return request({
        url: "/wap/seller/report/head",
        method: METHODS.POST,
        data
    })
}

export const sellerInstrumentPanelHead = (data) => {
  return request({
      url: "/wap/seller/instrument-panel/head",
      method: METHODS.POST,
      data
  })
}

export const sellerInstrumentPanelLine = (data) => {
  return request({
      url: "/wap/seller/instrument-panel/line",
      method: METHODS.POST,
      data
  })
}

export const sellerInstrumentPanelStats = (data) => {
  return request({
      url: "/wap/seller/instrument-panel/stats",
      method: METHODS.POST,
      data
  })
}

export const sellerGoodsList = (data) => {
  return request({
      url: "/wap/seller/goods/list",
      method: METHODS.POST,
      data
  })
}
export const sellerInfo = (data) => {
  return request({
      url: "/wap/seller/seller/info",
      method: METHODS.POST,
      data
  })
}

export const sellerUpdate = (data) => {
  return request({
      url: "/wap/seller/seller/update",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotional = (data) => {
  return request({
      url: "/wap/seller/promotional/my",
      method: METHODS.POST,
      data
  })
}

export const promoteLevel = (data) => {
  return request({
    url: "/api/promote/team-level",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotionalTeam = (data) => {
  return request({
      // url: "/api/seller/promotional/team-level",
      url: "/api/promote/team-level",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotionalView = (data) => {
  return request({
      url: "/wap/seller/promotional/view",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotionalBuy = (data) => {
  return request({
      url: "/wap/seller/promotional/buy",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotionalListBuy = (data) => {
  return request({
      url: "/wap/seller/promotional/listBuy",
      method: METHODS.POST,
      data
  })
}

export const categoryGoodCount = (data) => {
  return request({
      url: "/wap/api/sellerGoods/categoryGoodCount",
      method: METHODS.POST,
      data
  })
}

export const categoryGoodList = (data) => {
  return request({
      url: "/wap/api/sellerGoods/categoryGoodList",
      method: METHODS.POST,
      data
  })
}

export const reportList = (data) => {
  return request({
      url: "/wap/seller/report/list",
      method: METHODS.POST,
      data
  })
}

export const cmsList = () => {
  return request({
      url: "/api/cms/",
      method: METHODS.GET
  })
}

export const malllevelList = () => {
  return request({
      url: "/wap/api/malllevel/levelList",
      method: METHODS.GET
  })
}

export const mallLevelBuy = (data) => {
  return request({
      loadingPass: true,
      url: "/wap/api/malllevel/levelBuy",
      method: METHODS.POST,
      data
  })
}

export const malllevelConfig = () => {
  return request({
      url: "/wap/api/malllevel/config",
      method: METHODS.GET
  })
}

export const sysParaSign = () => {
  return request({
      url: "/wap/api/sysParaSign/info",
      method: METHODS.GET
  })
}
