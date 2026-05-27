import zhLocale from 'element-ui/lib/locale/lang/zh-CN'
import home from './china/home'

const cn = {
    language: '简体中文',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': "手机号码最小长度为8位。",
    '邮箱账号名称最小长度为6位': "邮箱账号名称最小长度为6位。",
    '邮箱只能包含英文，数字等字符': "邮箱只能包含英文，数字等字符",
    '请选择正确的收货地址': "请选择正确的收货地址。",
    ...zhLocale
}

export default cn
