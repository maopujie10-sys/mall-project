import trLocale from 'element-ui/lib/locale/lang/tr-TR'
import home from './tr/home'

const tr = {
    language: 'Русский',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': 'Cep telefonu numarasının minimum uzunluğu 8 hanedir',
    '邮箱账号名称最小长度为6位': 'E-posta hesap adının minimum uzunluğu 6 karakterdir',
    '邮箱只能包含英文，数字等字符': "Posta kutusu yalnızca İngilizce ve sayılar gibi karakterler içerebilir",
    '请选择正确的收货地址': 'Lütfen doğru gönderim adresini seçin',
    ...trLocale
}
export default tr
