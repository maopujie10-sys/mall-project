import enLocale from 'element-ui/lib/locale/lang/en'
import home from './english/home'

const en = {
    language: 'English',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': "The minimum length of the mobile phone number is 8 digits.",
    '邮箱账号名称最小长度为6位': "The minimum length of the email account name is 6 characters.",
    '邮箱只能包含英文，数字等字符': "The Email can only contain English, numbers and other characters",
    '请选择正确的收货地址': "Please select the correct delivery address.",
    ...enLocale
}

export default en
