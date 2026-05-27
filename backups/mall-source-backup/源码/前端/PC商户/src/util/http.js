import axios from "axios";
import URL from "../config/index";
import { Message } from "element-ui";
import allTits from "../assets/lan/tits.js";
import router from "../router.js";
import store from "../store";
import { ES_TOKEN, ES_LANGUAGE_MAP } from "@/common/constant";
const axiosInstance = axios.create({
  baseURL: URL.BASE_URL,
  timeout: 15000,
  // headers: {'X-Custom-Header': 'foobar'}
});
// axios.defaults.timeout = 15000;
// axios.defaults.baseURL = URL.BASE_URL;
console.log('ES_LANGUAGE_MAP ->', ES_LANGUAGE_MAP);
const requestLangMap = {
  [ES_LANGUAGE_MAP.zhCN]: "cn",
  [ES_LANGUAGE_MAP.zhTW]: "tw",
  [ES_LANGUAGE_MAP.en]: "en",
  [ES_LANGUAGE_MAP.ja]: "ja",
  [ES_LANGUAGE_MAP.de]: "de",
  [ES_LANGUAGE_MAP.ms]: "ms",
  [ES_LANGUAGE_MAP.af]: "af",
  [ES_LANGUAGE_MAP.th]: "th",
  [ES_LANGUAGE_MAP.el]: "el",
  [ES_LANGUAGE_MAP.pt]: "pt",
  [ES_LANGUAGE_MAP.es]: "es",
  [ES_LANGUAGE_MAP.fr]: "fr",
  [ES_LANGUAGE_MAP.ru]: "ru",
  [ES_LANGUAGE_MAP.it]: "it",
  [ES_LANGUAGE_MAP.tr]: "tr",
  [ES_LANGUAGE_MAP.ko]: "ko",
  [ES_LANGUAGE_MAP.ph]: "ph",
  [ES_LANGUAGE_MAP.ar]: "ar",
  [ES_LANGUAGE_MAP.id]: "id",
  [ES_LANGUAGE_MAP.hi]: "hi",
  [ES_LANGUAGE_MAP.vi]: "vi",
};
export const getCurrentLang = () => {
  const lang = store.getters.currentLang;
  return { lang: requestLangMap[lang] };
};

const handlerPostParams = (url, data) => {
  if (Object.keys(data).length) {
    for (let i in data) {
      url += url.indexOf("?") < 0 ? `?${i}=${data[i]}` : `&${i}=${data[i]}`;
    }
  }
  return url;
};
//http request 拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(ES_TOKEN);
    // config.data = JSON.stringify(config.data);
    // config.headers = {
    //   'Content-Type':'application/x-www-form-urlencoded'
    // }
    if (config.method == "get") {
      token && (config.params.token = token);
    } else if (config.method == "post") {

      if (config.data.body) {
        config.url = handlerPostParams(config.url, { token, ...config.data.params });
        config.data = config.data.body;
      } else {
        token && (config.data.token = token);
        config.url = handlerPostParams(config.url, config.data);
        config.data = null;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

let msgsCache = {};

//http response 拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    if (response.data.code != 0) {
      var localLan = store.getters.currentLang,
        lanTits = "";
      if (localLan == ES_LANGUAGE_MAP.en) {
        lanTits = "tits_en";
      } else if (localLan == ES_LANGUAGE_MAP.zhCN) {
        lanTits = "tits_zh-CN";
      } else if (localLan == ES_LANGUAGE_MAP.zhTW) {
        lanTits = "tits_CN";
      } else if (localLan == ES_LANGUAGE_MAP.ja) {
        lanTits = "tits_ja";
      } else if (localLan == ES_LANGUAGE_MAP.de) {
        lanTits = "tits_de";
      } else if (localLan == ES_LANGUAGE_MAP.ms) {
        lanTits = "tits_ms";
      } else if (localLan == ES_LANGUAGE_MAP.af) {
        lanTits = "tits_af";
      } else if (localLan == ES_LANGUAGE_MAP.th) {
        lanTits = "tits_th";
      } else if (localLan == ES_LANGUAGE_MAP.el) {
        lanTits = "tits_el";
      } else if (localLan == ES_LANGUAGE_MAP.pt) {
        lanTits = "tits_pt";
      } else if (localLan == ES_LANGUAGE_MAP.es) {
        lanTits = "tits_es";
      } else if (localLan == ES_LANGUAGE_MAP.fr) {
        lanTits = "tits_fr";
      } else if (localLan == ES_LANGUAGE_MAP.ru) {
        lanTits = "tits_ru";
      } else if (localLan == ES_LANGUAGE_MAP.it) {
        lanTits = "tits_it";
      } else if (localLan == ES_LANGUAGE_MAP.tr) {
        lanTits = "tits_tr";
      } else if (localLan == ES_LANGUAGE_MAP.ko) {
        lanTits = "tits_ko";
      } else if (localLan == ES_LANGUAGE_MAP.ph) {
        lanTits = "tits_ph"
      } else if (localLan == ES_LANGUAGE_MAP.ar) {
        lanTits = "tits_ar"
      } else if (localLan == ES_LANGUAGE_MAP.vi) {
        lanTits = "tits_vi"
      } else if (localLan == ES_LANGUAGE_MAP.id) {
        lanTits = "tits_id"
      } else if (localLan == ES_LANGUAGE_MAP.hi) {
        lanTits = "tits_hi"
      }
      if(response.config.url.indexOf("/api/rechargeBlockchain!recharge.action?") != -1 || response.config.url.indexOf('api/thirdPartyRecharge!recharge.action')!=-1){
        console.log('router ->', router);
        setTimeout(()=>{
          router.push("/userInfo/money-package");
        },2500)
      }


      if (response.data.code == "403") {
        localStorage.removeItem(ES_TOKEN);
        store.commit("SETUSERINFO", {});
        if (router.currentRoute.path !== "/") {
          router.push("/");
        }
      }
      const msg = response.data.msg;
      
      msgsCache[msg] && clearTimeout(msgsCache[msg])
      msgsCache[msg] = setTimeout(() => {
        const messages = allTits[lanTits]?.[msg] || msg
        msgsCache[msg] = undefined
       
        Message({
          message: messages,
          type: "error",
        })
      }, 500)

      return Promise.reject(response);
    }
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * 封装get方法
 * @param url
 * @param data
 * @returns {Promise}
 */
export function fetch(url, params = {}) {
  params = { ...params, ...getCurrentLang() };
  return new Promise((resolve, reject) => {
    axiosInstance
      .get(url, {
        params: params,
      })
      .then((response) => {
        resolve(response.data);
      })
      .catch((err) => {
        reject(err);
      });
  });
}

/**
 * 封装post请求
 * @param url
 * @param data
 * @returns {Promise}
 */

export function post(url, data = {}) {
  data = { ...data, ...getCurrentLang() };
  return new Promise((resolve, reject) => {
    axiosInstance.post(url, data).then(
      (response) => {
        resolve(response.data);
      },
      (err) => {
        reject(err);
      }
    );
  });
}

export function postBody(url, data = {}) {
  data = { params: getCurrentLang(), body: data };
  return new Promise((resolve, reject) => {
    axiosInstance.post(url, data).then(
      (response) => {
        resolve(response.data);
      },
      (err) => {
        reject(err);
      }
    );
  });
}

/**
 * 封装patch请求
 * @param url
 * @param data
 * @returns {Promise}
 */

export function patch(url, data = {}) {
  data = { ...data, ...getCurrentLang() };
  return new Promise((resolve, reject) => {
    axiosInstance.patch(url, data).then(
      (response) => {
        resolve(response.data);
      },
      (err) => {
        reject(err);
      }
    );
  });
}

/**
 * 封装put请求
 * @param url
 * @param data
 * @returns {Promise}
 */

export function put(url, data = {}) {
  data = { ...data, ...getCurrentLang() };
  return new Promise((resolve, reject) => {
    axiosInstance.put(url, data).then(
      (response) => {
        resolve(response.data);
      },
      (err) => {
        reject(err);
      }
    );
  });
}
export default { fetch, patch, put, post, postBody };
