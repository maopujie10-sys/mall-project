import router from '@/router'
import dayjs from "dayjs";
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import moment from "moment-timezone";
import { useSystemStore } from "@/store/system.js";

dayjs.extend(utc)
dayjs.extend(timezone)

export function getImageUrl(path) {
  return new URL(path, import.meta.url).href
}

// 设置localStorage
export const setStorage = function (key, obj) {
  let json = JSON.stringify(obj)
  window.localStorage.setItem(key, json)
  // console.log('设置语言', key, json)
}

// 获取localStorage
export const getStorage = function (key) {
  const str = window.localStorage.getItem(key)
  if (!str) {
    return null
  }
  return JSON.parse(str)
}
// 获取浏览器默认语言
export const getBrowserLang = function () {
  let browserLang = navigator.language ? navigator.language : navigator.browserLanguage
  let defaultBrowserLang = ''
  if (browserLang.toLowerCase() === 'cn' || browserLang.toLowerCase() === 'zh' || browserLang.toLowerCase() === 'zh-cn') {
    defaultBrowserLang = 'cn'
  } else {
    defaultBrowserLang = 'en'
  }
  return defaultBrowserLang
}

export const dataTime = (data, isTrue, mHide) => {
  var date = new Date(data);
  let Y = date.getFullYear() + '-';
  let M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
  let D = (date.getDate() < 10 ? '0' + date.getDate() : date.getDate()) + ' ';
  let h = (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':';
  let m = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes());
  let s = date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds()
  let str = Y + M + D
  if (isTrue) {
    if (mHide) {
      str = Y + M + D + h + m
    } else {
      str = Y + M + D + h + m + ':' + s
    }
  } else {
    str = Y + M + D
  }
  return str
}

// 路由跳转
export function openPage(data, blank) {
  if (blank) {
    if (typeof data === 'string') {
      window.open(data)
    } else {
      const routeData = router.resolve(data)
      window.open(routeData.href)
    }
  } else {
    router.push(data)
  }
}

// 复制 TODO: 实现
export const clipboardText = () => {
  console.log('test')
}

// 下载图片
export const downloadFile = (imgsrc, name) => {
  const image = new Image();
  image.setAttribute('crossOrigin', 'anonymous');
  image.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = image.width;
    canvas.height = image.height;
    const context = canvas.getContext('2d');
    // @ts-ignore
    context.drawImage(image, 0, 0, image.width, image.height);
    const url = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    const event = new MouseEvent('click');
    a.download = name || 'photo';
    a.href = url;
    a.dispatchEvent(event);
  };
  image.src = imgsrc
}

/**
 * 数字千位符格式化
 * eg:
 * 17267737 -> 17,267,737
 */
export function numberFormat(num) {
  const numStr = num.toFixed(2)
  const numPre = numStr.slice(0, numStr.indexOf('.'))
  const numRi = numStr.slice(numStr.indexOf('.') + 1)
  const intStr = numPre.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,")
  const floatStr = numRi === '00' ? '' : `.${numRi}`

  return `${intStr}${floatStr}`
}

export function convertTimeZone(time) {
  console.log(time);
  const time1 = dayjs(time).tz('Asia/Shanghai')
  const time2 =  dayjs(time1).tz(dayjs.tz.guess())
  console.log(time2);
  return time2.format('YYYY-MM-DD HH:mm:ss')
}

// 当地时间
export const formatZoneDate = (time, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!time) return '--'
  //设置服务器默认时区
  // moment.tz.setDefault('Asia/Shanghai')
  // time = moment(time)
  // //获取当前时区
  // let timezone = moment.tz.guess(true)
  // //time转成当前时区的时间
  // time = moment.tz(time, timezone).format(format)
  // return time
  return moment(time).format(format)
}

export const formeateUser = (name, flag = true, chat = false) => {
  const mode = import.meta.env.MODE || 'test'
  if (/^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/.test(name) && name.indexOf('@') > -1) {
    const split = name.split('@')
    if (flag) {
      return `${mode} ***@${split[1]}`
    } else {
      const txt = split[0]
      let txtStr = ''
      if (txt.length < 3) {
        txtStr = chat ? txt.substring(0, 2) + '*' : txt.substring(0, 1) + '*'
      } else {
        txtStr = chat ? txt.substring(0, 2) + '**' : txt.substring(0, 1) + '***' + txt.substring(txt.length - 1)
      }
      return `${txtStr}@${split[1]}`
    }
  } else {
    const len = name.length
    let namStr = ''
    if (len === 1) {
      namStr = '*'
    } else if (len === 2) {
      namStr = name.substring(0, 1) + '*'
    } else if (len === 3) {
      namStr = name.substring(0, 1) + '**'
    } else if (len < 7) {
      namStr = name.substring(0, 2) + '***' + name.substring(name.length - 2)
    } else {
      namStr = name.substring(0, 2) + '****' + name.substring(name.length - 2)
    }
    return flag ? `${mode}  ${namStr}` : namStr
  }
}

// 数字格式化
export const numberStrFormat = (number, decimal = 2, flag = false) => {
  let resStr = decimal === 0 ? 0 : '0.00'
  const amount = Number(number)
  if (!isNaN(amount)) {
    const options = {
      minimumFractionDigits: decimal ? decimal + 3 : 0
    }
    resStr = flag ? String(amount) : Math.abs(amount).toLocaleString('en-US', options)
    if (resStr.indexOf('.') > -1) {
      const arr = resStr.split('.')
      if (arr[1].length === 1) {
        resStr = resStr + '0'
      }
      if (arr[1].length > 2 && decimal === 2) {
        resStr = arr[0] + '.' + arr[1].slice(0, 2)
      }
    } else {
      resStr = decimal === 0 ? resStr : resStr + '.00'
    }
  }
  return !isNaN(amount) && amount < 0 ? '-' + resStr : resStr
}

// 进入客服中心
export const openService = (flag = false) => {
  const mode = import.meta.env.MODE 
  const systemStore = useSystemStore()
  const customer_service_url = systemStore?.customer_service_url || ''
  const path = customer_service_url ? '/customerServiceOther' : '/customerService'
  if (!flag) {
    if(['familyShop'].includes(mode)) {
      im_create_iframe_client.open();
    } else {
      router.push(path)
    }
  } else {
    if (customer_service_url) {
      if (window.plus) {
        window.plus.runtime.openURL(customer_service_url)
      } else if (window.webkit) {
        window.webkit.messageHandlers.openWindow.postMessage({url: customer_service_url})
      } else {
        window.open(customer_service_url)
      }
    } else {
      const {hostname, origin} = window.location
      let href = ''
      if (isMobile()) {
        href = hostname === 'localhost' ? 'https://www.catvg.xyz/www/#/customerService' : `${origin}/www/#/customerService`
      } else {
        href = hostname === 'localhost' ? 'https://www.catvg.xyz/ww/#/login' : `${origin}/ww/#/login`
      }

      if(['familyShop'].includes(mode)) {
        im_create_iframe_client.open();
      } else {
        if (window.plus) {
          window.plus.runtime.openURL(href)
        } else if (window.webkit) {
          window.webkit.messageHandlers.openWindow.postMessage({url: href})
        } else {
          window.open(href)
        }
      }
    }
  }
}

// 图片引入
export const getImg = (filePath) => {
  const img = new URL(`../assets/${filePath}`, import.meta.url)
  return img ? img.href : ''
}

// 判断是否为手机端
export const isMobile = () => {
  const uA = navigator.userAgent.toLowerCase();
  const ipad = uA.match(/ipad/i) == "ipad";
  const iphone = uA.match(/iphone os/i) == "iphone os";
  const midp = uA.match(/midp/i) == "midp";
  const uc7 = uA.match(/rv:1.2.3.4/i) == "rv:1.2.3.4";
  const uc = uA.match(/ucweb/i) == "ucweb";
  const android = uA.match(/android/i) == "android";
  const windowsce = uA.match(/windows ce/i) == "windows ce";
  const windowsmd = uA.match(/windows mobile/i) == "windows mobile";
  if (!(ipad || iphone || midp || uc7 || uc || android || windowsce || windowsmd)) {
    return false
    
  } else{
    return true
  }
}

// 跳过某些全局方法
export const isPassPage = () => {
  const whiteHash = ['login-agreement']
  const hash = window.location.hash

  for (let i = 0; i < whiteHash.length; i++) {
    if (hash.indexOf(whiteHash[i]) > -1) {
      return true
    }
  }
  return false
}

export const loadJs = (src) => {
  return new Promise((resolve, reject) => {
      let script = document.createElement('script');
      script.type = "text/javascript";
      script.src = src;
      document.body.appendChild(script);

      script.onload = () => {
          resolve();
      }
      script.onerror = () => {
          reject();
      }
  })
}

// 日期时间格式化
export const dateFormat = (date, format = "") => {
  if (!date) return ''
  const _date = new Date(date)
  let _format = format || 'yyyy-MM-dd hh:mm:ss'
  const o = {
      "M+": _date.getMonth() + 1, //month
      "d+": _date.getDate(), //day
      "h+": _date.getHours(), //hour
      "m+": _date.getMinutes(), //minute
      "s+": _date.getSeconds(), //second
      "q+": Math.floor((_date.getMonth() + 3) / 3), //quarter
      "S": _date.getMilliseconds() //millisecond
  }
  if (/(y+)/.test(_format)) {
      _format = _format.replace(RegExp.$1, (_date.getFullYear() + "").substr(4 - RegExp.$1.length))
  }
  for (let k in o) {
      if (new RegExp("(" + k + ")").test(_format)) {
          _format = _format.replace(RegExp.$1, RegExp.$1.length == 1
              ? o[k]
              : ("00" + o[k]).substr(("" + o[k]).length))
      }
  }
  return _format
}

// 除去首位空格
export const trim = (str) => {
  return str.replace(/(^\s*)|(\s*$)/g, "");
}
