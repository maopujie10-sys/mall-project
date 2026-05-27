import { isFunction, omit, isArray } from 'lodash'
import i18n from "@/lang/i18n";

class RuleUtilsSuper {
  static rulesMap = {}
  /**
   * 获取校验规则方法
   * @template { keyof RulesMap } T
   * @template {typeof RuleUtils} C
   * @param {T} name 类型名， 与ruleConfig的key值对应
   * @param { undefined | null | string } message 校验失败的错误消息
   * @param {RulesOptions} options 其他配置项，用于拓展
   * @param {C} context 规则枚举变量
   * @return {RuleItem}
   */
  static getRule(name, message, options = {}, context = {}) {
    const rulesMap = context.rulesMap ?? this.rulesMap
    const transform = context.transform ?? this.transform
    // 判断获取的规则是否存在
    if (Object.keys(rulesMap).includes(name) && isFunction(rulesMap[name])) {
      // dynamic 参数用于动态传值
      const { dynamic = {} } = options

      const res = rulesMap[name](dynamic)

      const dist = {
        trigger: ['blur', 'change'],
        ...res,
        ...omit(options, 'dynamic')
      }

      if (message) {
        dist.message = message
      }
      // transform null  v => v 都会有影响
      if (transform) {
        dist.transform = transform
      }
      return dist
    }
    // 为空 async-validate 不会进行校验
    return {}
  }

  static transform = null
}

/**
 * 规则对象
 */
export const rulesMap = {
  /**
   * ---------------------------------------- 特殊处理场景 --------------------------------------------
   */
  // 必填项不能为空
  required: () => ({
    required: true,
    message: i18n.t('message.home.validatorRequire')
  }),
  // 自定义校验
  validator: arg => ({ ...arg }),
  /**
   * ---------------------------------------- 正则方法 --------------------------------------------
   */
  // 手机号验证
  phone: () => ({
    pattern: /^[\d]{1,20}$/,
    message: i18n.t('message.home.validatorPhone')
  }),
  //邮箱账号验证
  email: () => ({
    pattern: /^([A-Za-z0-9_\-\.\w{3,}])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/,
    message: i18n.t('message.home.validatorEmail')
  }),
  // 登录密码-验证 (密码长度为6到20位，仅支持大小写的英文字母，数字和特殊字符，且最少包含一个字母或者特殊字符) 【ASCII码 33 - 126】
  password: () => ({
    pattern: /^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;'"\\|,.<>?~`\-=/]{6,12}$/,
    message: i18n.t('message.home.validatorPassword')
  }),
  //请输入6位纯数字
  sixNumber: () => ({
    pattern: /^\d{6}$/,
    message: i18n.t('message.home.validatorSixNumber')
  }),
  //请输入4位以上纯数字
  fourMoreNumber: () => ({
    pattern: /^[0-9A-Za-z]{4,32}$/,
    message: i18n.t('message.home.validatorFourMoreNumber')
  }),
  // 请输入大于0的数字 (含小数)
  decimalExceedZero: () => ({
    pattern: /^(([1-9]\d+)|[1-9])(\.\d{1,2})?$/,
    message: i18n.t('message.home.充值金额不能小于1')
  }),
  // 输入包含小数点后六位的数字
  decimalSix: () => ({
    pattern: /^\d+(\.\d{1,10})?$/,
    message: i18n.t('message.home.最多包含10位小数')
  }),
  // IP地址验证
  ipAddress: () => ({
    pattern: /^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$/,
    message: i18n.t('message.home.validatorIpRule')
  }),

  cionAddress: () => ({
    pattern: /[^\u4E00-\u9FA5]/g,
    message: i18n.t('message.home.pleaseCorrectAddress')
  }),
  /**
   * ---------------------------------------- 以下为动态参数方法 --------------------------------------------
   */
  // 中英文,支持动态数量 (仅支持中英文,输入范围${cStart}-${cEnd}个字符)
  chineseAndEnglishValidate: ({ cStart = 1, cEnd = 32 }) => ({
    pattern: new RegExp(`^[\\u4E00-\\u9FA5a-z]{${cStart},${cEnd}}$`, 'i'),
    message: i18n.t('message.home.validatorChineseAndEnglish', { cStart, cEnd })
  }),
}

function myTransform(value) {
  if (isArray(value)) {
    Object.assign(this, { type: 'array' })
    return value
  }
  return value?.toString()?.trim() ?? ''
}


class RuleUtils extends RuleUtilsSuper {
  /**
   * @param {keyMap} name
   * @param {Parameters<typeof RuleUtilsSuper.getRule>[1] } message
   * @param {Parameters<typeof RuleUtilsSuper.getRule>[2] } options
   */
  static getRule(name, message, options = {}) {
    return RuleUtilsSuper.getRule(name, message, options, {
      rulesMap,
      transform: myTransform
    })
  }

  /**
   * 复用规则
   */
  static rulesMap = rulesMap
}
export default RuleUtils