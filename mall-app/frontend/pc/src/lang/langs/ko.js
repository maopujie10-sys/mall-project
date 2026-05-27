import koLocale from 'element-ui/lib/locale/lang/ko'
import home from './ko/home'

const ko = {
    language: '한국어',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': '휴대전화 번호의 최소 길이는 8자리입니다',
    '邮箱账号名称最小长度为6位': "이메일 계정 이름의 최소 길이는 6자입니다",
    '邮箱只能包含英文，数字等字符': "우편함은 영문, 숫자 등의 문자만 포함할 수 있습니다",
    '请选择正确的收货地址': "올바른 배송 주소를 선택하세요",
    ...koLocale
}
export default ko
