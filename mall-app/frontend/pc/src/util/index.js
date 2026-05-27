import { getCurrentLang } from './http'
import config from '../config'
import store from '../store'
import { number } from 'mathjs';
// 日期格式化
export const dateFormat = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  const dateTime = new Date(date);
  const o = {
    'M+': dateTime.getMonth() + 1, // month
    'D+': dateTime.getDate(), // day
    'H+': dateTime.getHours(), // hour
    'm+': dateTime.getMinutes(), // minute
    's+': dateTime.getSeconds(), // second
    'q+': Math.floor((dateTime.getMonth() + 3) / 3), // quarter
    S: dateTime.getMilliseconds() // millisecond
  };
  if (/(Y+)/.test(format)) {
    format = format.replace(RegExp.$1, `${dateTime.getFullYear()}`.substr(4 - RegExp.$1.length));
  }

  Object.keys(o).forEach((k) => {
    if (new RegExp(`(${k})`).test(format)) {
      format = format.replace(RegExp.$1, RegExp.$1.length === 1 ? o[k] : `00${o[k]}`.substr(`${o[k]}`.length));
    }
  });
  return format;
};

/**
 * 数字千位符格式化
 * eg:
 * 17267737 -> 17,267,737
 */
export const numberFormat = (num) => {
  if (num && Number(num)) {
    const numStr = TtoFixed(num, 2)
    const numPre = numStr.slice(0, numStr.indexOf('.'))
    const numRi = numStr.slice(numStr.indexOf('.') + 1)
    const intStr = numPre.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,")
    const floatStr = numRi ? `.${numRi.length < 2 ? numRi + '0' : numRi}` : '.00'
    return `${intStr}${floatStr}`
  } else {
    return '0.00'
  }
}
export const numberFormatA = (num) => {
  if (num && Number(num)) {
    const numStr = TtoFixed(num, 2)
    const numPre = numStr.slice(0, numStr.indexOf('.'))
    // const numRi = numStr.slice(numStr.indexOf('.') + 1)
    const intStr = numPre.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,")
    // const floatStr = numRi ? `.${numRi.length < 2 ? numRi + '0' : numRi}` : ''
    return `${intStr}`
  } else {
    return '0'
  }
}
const TtoFixed = (num, decimal) => {
  num = num.toString();
  let index = num.indexOf('.');
  if (index !== -1) {
    num = num.substring(0, decimal + index + 1)
  } else {
    num = num.substring(0)
  }
  return parseFloat(num).toFixed(decimal)
}

/*
 * 格式化电话号码
 * 参数说明：
 * num：要格式化的电话号码
 * */
export function phoneNumber(num) {
  if (num) {
    return num.substring(0, 3) + "*****" + num.substring(8, 11);
  }
  return "";
}

/**
 * 将字符串复制到剪贴板
 * @param {string} text
 */
export function copyTextToClipboard(text) {
  if (navigator.clipboard) {
    // clipboard api 复制
    navigator.clipboard.writeText(text);
  } else {
    const textarea = document.createElement("textarea");
    document.body.appendChild(textarea);
    textarea.style.position = "fixed";
    textarea.style.clip = "rect(0 0 0 0)";
    textarea.style.top = "10px";
    textarea.value = text;
    textarea.select();
    document.execCommand("copy", true);
    document.body.removeChild(textarea);
  }
}

export function downloadImage(url) {
  const a = document.createElement("a");
  document.body.appendChild(a);
  a.style.position = "fixed";
  a.style.clip = "rect(0 0 0 0)";
  a.style.top = "10px";
  a.href = url;
  a.download = url;
  a.click();
  document.body.removeChild(a);
}

// 将file文件上传转化为base64进行显示
export function getBase64(file) {
  return new Promise((resolve, reject) => {
    ///FileReader类就是专门用来读文件的
    const reader = new FileReader();
    //开始读文件
    //readAsDataURL: dataurl它的本质就是图片的二进制数据， 进行base64加密后形成的一个字符串，
    reader.readAsDataURL(file);
    // 成功和失败返回对应的信息，reader.result一个base64，可以直接使用
    reader.onload = () => resolve(reader.result);
    // 失败返回失败的信息
    reader.onerror = (error) => reject(error);
  });
}

export function emptyStr(str) {
  return !str || str.trim() === ""
}

export function openChatPage(token = "", partyId = "", name = "", productId = "") {
  // const token = localStorage.getItem(ES_TOKEN);
  const avatar = store.getters.userInfo.avatar;
  window.open(`${config.HOST_URL}/chat/#/pc/yellow?token=${token}&partyid=${partyId}&name=${name}&lang=${getCurrentLang().lang}&selfimg=${avatar}&productId=${productId}`, '_blank')

}


export function debounce(func, wait = 500) {
  let timeout;

  return function () {
    let context = this; // 保存this指向
    let args = arguments; // 拿到event对象

    clearTimeout(timeout)
    timeout = setTimeout(function () {
      func.apply(context, args)
    }, wait);
  }
}

/**
 * @param {string} path
 * @returns {Boolean}
 */
export function isExternal(path) {
  return /^(https?:|mailto:|tel:)/.test(path)
}