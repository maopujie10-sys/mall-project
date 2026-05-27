/**
 * 精度计算工具
 */
import BigNumber from 'bignumber.js'
// 精确浮点运算的三方库

/**
 * @加法
 * @params 数字 add(0.1, 0.2) => 0.3
 * @type:numbert 类型
 */
export function accAdd(a, b) {
  return new BigNumber(a).plus(new BigNumber(b)).toNumber()
}

/**
 * @减法
 * @params 数字 minus(0.1, 0.11) =>  -0.01
 * @type:numbert 类型
 */
export function accMinus(a, b) {
  return new BigNumber(a).minus(new BigNumber(b)).toNumber()
}

/**
 * 除法
 * @param {nunbert} a 数字 div(13, 1.6)
 * @param {nunbert} b 数字 div(13, 1.6)
 */
export function accDiv(a, b) {
  return new BigNumber(a).div(new BigNumber(b)).toNumber()
}

/**
 * 乘法
 * @params 数字 times(1,2)
 * @type:numbert 类型
 */
export function accTimes(a, b) {
  return new BigNumber(a).multipliedBy(new BigNumber(b)).toNumber()
}

// 递归运算，支持3个以上的多参数运算
const countReduce = (func, ...args) => {
  return args.reduce((count, item, index) => {
    if (index === 0) return count
    count = func(count, item)
    return count
  }, args[0])
}

/**
 * 导出加减乘除
 * @use add(100,10,2) | minus(10,5,3) | times(10,2,3) | div(100,5,2)
 * @param {number} 参数的数据类型必须是 number
 * @return {number} 计算结果
 */
export const add = (...args) => countReduce(accAdd, ...args)
export const minus = (...args) => countReduce(accMinus, ...args)
export const times = (...args) => countReduce(accTimes, ...args)
export const div = (...args) => countReduce(accDiv, ...args)

/**
 * 安全的代替Math.random的方法
 * @returns {number} a crypto-random number >= 0 and < 1 (not <=).
 */
export const random = () => {
  try {
    const randomBuffer = new Uint32Array(1)
    ;(window.crypto || window.msCrypto).getRandomValues(randomBuffer)
    return randomBuffer[0] / (0xffffffff + 1)
  } catch (error) {
    return Math.random()
  }
}
