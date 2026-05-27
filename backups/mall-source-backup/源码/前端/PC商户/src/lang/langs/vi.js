import viLocale from 'element-ui/lib/locale/lang/vi'
import home from './vi/home'

const vi = {
    language: 'Tiếng Việt',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': 'Độ dài tối thiểu của số điện thoại di động là 8 chữ số',
    '邮箱账号名称最小长度为6位': 'Độ dài tối thiểu của tên tài khoản email là 6 ký tự',
    '邮箱只能包含英文，数字等字符': 'Email chỉ có thể chứa tiếng Anh, số và các ký tự khác',
    '请选择正确的收货地址': 'Vui lòng chọn địa chỉ giao hàng chính xác',
    ...viLocale
}
export default vi
