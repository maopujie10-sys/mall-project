/**
 * 处理购物车相关存储问题
 */

import i18n from "@/lang/i18n";
import Dexie from "dexie";

import { ES_SHOP_CART, ES_VUEX, ES_TOKEN, ES_SEARCH_HISTORY } from '@/common'
import store from '@/store'

// import Dexie from 'dexie';

const db = new Dexie("es-shop-cart");

db.version(1).stores({
  esLocalStore: '++id, key, value', // 创建一个名为esLocalStore的数据表
});


const getShopKey = async () => {
  const getKeyByLocal = async () => {
    const esLocal = await db.esLocalStore.where({ key: ES_VUEX }).first();
    if (esLocal) {
      const parseEsLocal = JSON.parse(esLocal.value) ?? {};
      const { userInfo } = parseEsLocal;
      if (userInfo && userInfo.usercode) {
        return `${ES_SHOP_CART}_${userInfo.usercode}`;
      }
    }
    return ES_SHOP_CART;
  };

  const isLogin = localStorage.getItem(ES_TOKEN);
  if (isLogin) {
    const usercode = store.getters.userInfo?.usercode;
    if (usercode) {
      return `${ES_SHOP_CART}_${usercode}`;
    }
  }

  return getKeyByLocal();
};

/**
 * 清理当前用户的购物车
 */
export const clearShopCartLocal = async () => {
  const KEY = await getShopKey();
  // 使用 Dexie 删除数据
  const esLocal = await db.esLocalStore.where({ key: KEY }).first();
  await db.esLocalStore.where({ key: KEY }).delete(esLocal.id);
}

/**
 * 设置购物车存储
 */
export const setShopCartLocal = async (values) => {
  const KEY = await getShopKey();
  console.log('values ->', values);
  console.log('getShopId() ->', getShopId());
  // 使用 Dexie 存储数据
  await db.esLocalStore.put({ key: KEY, value: JSON.stringify(values) });
}

/**
 * 获取购物车储存
 */
export const getShopCartLocal = async () => {
  const KEY = await getShopKey();
  console.log('KEY111 ->', KEY);

  // 使用 Dexie 获取数据
  const esLocal = await db.esLocalStore.where({ key: KEY }).first();
  console.log('esLocal ->', esLocal);
  if (esLocal) {
    const parseEsLocal = JSON.parse(esLocal.value) ?? [];
    console.log('parseEsLocal ->', parseEsLocal);
    return parseEsLocal;
  }
  return [];
}

// const getShopKey = () => {
//   const getKeyByLocal = () => {
//     const esLocal = localStorage.getItem(ES_VUEX)
//     if (esLocal) {
//       const parseEsLocal = JSON.parse(esLocal) ?? {}
//       const { userInfo } = parseEsLocal
//       if (userInfo && userInfo.usercode) {
//         return `${ES_SHOP_CART}_${userInfo.usercode}`
//       }
//     }
//     return ES_SHOP_CART
//   }
//   const isLogin = localStorage.getItem(ES_TOKEN);
//   if (isLogin && store && store.getters) {
//     const usercode = store.getters.userInfo?.usercode
//     if (usercode) {
//       return `${ES_SHOP_CART}_${usercode}`
//     }
//   }
//   return getKeyByLocal()
// }

/**
 * 获取搜索历史储存
 */
export const getSearchHistoryLocal = () => {
  const KEY = getSearchHistoryKey()
  const data = localStorage.getItem(KEY)
  return !!data ? JSON.parse(data) : []
}



/**
 * 设置搜索历史存储
 */
export const setSearchHistoryLocal = (values) => {
  const KEY = getSearchHistoryKey()
  localStorage.setItem(KEY, JSON.stringify(values))
}



const getSearchHistoryKey = () => {
  const getKeyByLocal = () => {
    const esLocal = localStorage.getItem(ES_VUEX)
    if (esLocal) {
      const parseEsLocal = JSON.parse(esLocal) ?? {}
      const { userInfo } = parseEsLocal
      if (userInfo && userInfo.usercode) {
        return `${ES_SEARCH_HISTORY}_${userInfo.usercode}`
      }
    }
    return ES_SEARCH_HISTORY
  }

  const isLogin = localStorage.getItem(ES_TOKEN);
  if (isLogin && store && store.getters) {
    const usercode = store.getters.userInfo?.usercode
    if (usercode) {
      return `${ES_SEARCH_HISTORY}_${usercode}`
    }
  }
  return getKeyByLocal()
}
/**
 * 清理当前用户的搜索历史
 */
export const clearSearchHistoryLocal = () => {
  const KEY = getSearchHistoryKey()
  localStorage.removeItem(KEY)
}

export function getOrderStatusLable(number) {
  //  status（-1=已取消）（0=待付款）（1=待发货）（2=已确认）（3=待收货）（4=已收获）（5=已评价）（6=退款)
  switch (number) {
    case -1:
      //已取消
      return i18n.t("message.home.cancelled");
    case 0:
      //待支付
      return i18n.t("message.home.pending");
    case 1:
    // return i18n.t("message.home.delivered");
    case 2:
      //待发货
      // return i18n.t("message.home.confirmed")
      return i18n.t("message.home.delivered");
    case 3:
      //待收货
      return i18n.t("message.home.receipt")
    case 4:
      //待评价
      return i18n.t("message.home.comment")
    case 5:
      // 已评价
      return i18n.t("message.home.rated")
    case 6:
      //退款/售后
      return i18n.t("message.home.refund")
  }

}