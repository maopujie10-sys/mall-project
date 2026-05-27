import request from './request'
import {METHODS} from "../config/index.js";

export const sellerReportHead = (data) => {
    return request({
        url: "/wap/seller/report!head.action",
        method: METHODS.POST,
        data
    })
}

export const sellerInstrumentPanelHead = (data) => {
  return request({
      url: "/wap/seller/instrument-panel!head.action",
      method: METHODS.POST,
      data
  })
}

export const sellerInstrumentPanelLine = (data) => {
  return request({
      url: "/wap/seller/instrument-panel!line.action",
      method: METHODS.POST,
      data
  })
}

export const sellerInstrumentPanelStats = (data) => {
  return request({
      url: "/wap/seller/instrument-panel!stats.action",
      method: METHODS.POST,
      data
  })
}

export const sellerGoodsList = (data) => {
  return request({
      url: "/wap/seller/goods!list.action",
      method: METHODS.POST,
      data
  })
}
export const sellerInfo = (data) => {
  return request({
      url: "/wap/seller/seller!info.action",
      method: METHODS.POST,
      data
  })
}

export const sellerUpdate = (data) => {
  return request({
      url: "/wap/seller/seller!update.action",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotional = (data) => {
  return request({
      url: "/wap/seller/promotional!my.action",
      method: METHODS.POST,
      data
  })
}

export const promoteLevel = (data) => {
  return request({
    url: "/wap/api/promote!team_level.action",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotionalTeam = (data) => {
  return request({
      // url: "/wap/seller/promotional!team_level.action",
      url: "/wap/api/promote!team_level.action",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotionalView = (data) => {
  return request({
      url: "/wap/seller/promotional!view.action",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotionalBuy = (data) => {
  return request({
      url: "/wap/seller/promotional!buy.action",
      method: METHODS.POST,
      data
  })
}

export const sellerPromotionalListBuy = (data) => {
  return request({
      url: "/wap/seller/promotional!listBuy.action",
      method: METHODS.POST,
      data
  })
}

export const categoryGoodCount = (data) => {
  return request({
      url: "/wap/api/sellerGoods!categoryGoodCount.action",
      method: METHODS.POST,
      data
  })
}

export const categoryGoodList = (data) => {
  return request({
      url: "/wap/api/sellerGoods!categoryGoodList.action",
      method: METHODS.POST,
      data
  })
}

export const reportList = (data) => {
  return request({
      url: "/wap/seller/report!list.action",
      method: METHODS.POST,
      data
  })
}

export const cmsList = () => {
  return request({
      url: "/wap/api/cms!get.action",
      method: METHODS.GET
  })
}

export const malllevelList = () => {
  return request({
      url: "/wap/api/malllevel!levelList.action",
      method: METHODS.GET
  })
}

export const mallLevelBuy = (data) => {
  return request({
      loadingPass: true,
      url: "/wap/api/malllevel!levelBuy.action",
      method: METHODS.POST,
      data
  })
}

export const malllevelConfig = () => {
  return request({
      url: "/wap/api/malllevel!config.action",
      method: METHODS.GET
  })
}

export const sysParaSign = () => {
  return request({
      url: "/wap/api/sysParaSign!info.action",
      method: METHODS.GET
  })
}
