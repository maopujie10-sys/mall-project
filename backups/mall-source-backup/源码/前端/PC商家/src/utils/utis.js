/*!
 * @author atongmu <zhounianlai@teacher.com.cn>
 * date 11/07/2019
 * description The project tool function file.
 */

/**
 * @description 时间格式处理
 */
export const formatData = (data) => {
    const thisData = formatTime(new Date(), "yyyy-MM-dd");
    const myData = data.substr(0, 10);
    if (thisData == myData) {
        const Time = data.substr(11, 5);
        return Time
    } else {
        if (thisData.substr(0, 4) == myData.substr(0, 4) && thisData != myData) {
            const Data = data.substr(5, 11);
            return Data
        } else {
            const Year = myData;
            return Year
        }
    }
}

/**
 * @description 时间格式转化
 * @param {String} date 日期
 * @param {String} fmt 需要的格式
 */
export const formatTime = (date, fmt) => {
    const o = {
        "M+": date.getMonth() + 1, // 月份
        "d+": date.getDate(), // 日
        "h+": date.getHours(), // 小时
        "m+": date.getMinutes(), // 分
        "s+": date.getSeconds(), // 秒
        "q+": Math.floor((date.getMonth() + 3) / 3), // 季度
        "S": date.getMilliseconds() // 毫秒
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (date.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (const k in o) {
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    }
    return fmt;
}

/**
 * @description 验证手机号格式是否正确
 * @param {String} mobile 电话号码
 */
export const checkMobileformat = mobile => /^1[345789]\d{9}$/.test(mobile);

/**
 * @description Array clear empty item.
 * @param {Array} array
 */
export const arrayClearEmptyItem = array => {
    return array.filter(item => item);
}

/**
 * @description 判断一个日期是过去还是未来
 * @param {String} d 要判断的日期
 * @returns past => false   future => true
 */
export const judgeDateIsPastOrFuture = (d) => {
    if (!d) {
        return false;
    }
    const nowDate = new Date();
    const nowTimeStamp = nowDate.getTime();
    const date = new Date(d.replace(/-/g, "/"));
    const dateTimeStamp = date.getTime();
    return nowTimeStamp < dateTimeStamp;
}

/**
 * @description 判断一个字符串中是否有重复的项（0-9, a-z, A-Z）
 * @param {String} str 判断的目标字符串
 * @returns {Boolean} true: 有重复项   false: 无重复项
 */
export const strIsReplace = str => {
    const passwordRule = /[0-9a-zA-Z]/;
    const arr = str.split("");
    for (let i = 0; i < arr.length; i++) {
        const element = arr[i];
        if (passwordRule.test(element)) {
            if (i === arr.length - 1) {
                return false;
            }
            if (str.includes(element, i + 1)) {
                return true;
            }
        }
    }
    return false;
}
// 设置localStorage
export const setStorage = function (key, obj) {
    const json = JSON.stringify(obj)
    window.localStorage.setItem(key, json)
}

// 获取localStorage
export const getStorage = function (key) {
    const str = window.localStorage.getItem(key)
    if (!str) {
        return null
    }
    return JSON.parse(str)
}

// 移除localStorage
export const removeStorage = function (key) {
    window.localStorage.removeItem(key)
}

// 获取浏览器默认语言
export const getBrowserLang = function () {
    const browserLang = navigator.language ? navigator.language : navigator.browserLanguage
    let defaultBrowserLang = ''
    if (browserLang.toLowerCase() === 'cn' || browserLang.toLowerCase() === 'zh' || browserLang.toLowerCase() === 'zh-cn') {
        defaultBrowserLang = 'zh-CN'
    } else if (browserLang.toLowerCase() === 'zh-tw' || browserLang.toLowerCase() === 'zh-hk') {
        defaultBrowserLang = 'zh-TW'
    } else if (browserLang.toLowerCase() === 'en' || browserLang.toLowerCase() === 'en-us') {
        defaultBrowserLang = 'en'
    } else if (browserLang.toLowerCase() === 'ko' || browserLang.toLowerCase() === 'ko-kr') {
        defaultBrowserLang = 'ko'
    }
    return defaultBrowserLang
}

//将list转换为json对象
export function getJson(list, key) {
    let json = {};
    if (list && list.length > 0) {
        for (let i = 0, temp, len = list.length; i < len; i++) {
            temp = list[i];
            json[temp[key]] = temp;
        }
    }
    return json;
}


//获取origin
export function getOrigin() {
    let hostname = location.hostname, prefx;
    if (hostname == "localhost" || hostname == "127.0.0.1") {
        prefx = "http://localhost";
    } else {
        prefx = location.origin;
    }
    return prefx;
}





