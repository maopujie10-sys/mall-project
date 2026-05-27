import zhLocale from 'element-ui/lib/locale/lang/ja'
import home from './ja/home'

const ja = {
    language: '日本語',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': "携帯電話番号の最小長は 8 桁です。",
    '邮箱账号名称最小长度为6位': "電子メール アカウント名の最小長は 6 文字です。",
    '邮箱只能包含英文，数字等字符': "メールボックスには英語や数字などの文字のみを含めることができます",
    '请选择正确的收货地址': '正しい配送先住所を選択してください',
    ...zhLocale
}

export default ja
