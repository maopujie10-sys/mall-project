import deLocale from 'element-ui/lib/locale/lang/de'
import home from './de/home'

const de = {
    language: 'Deutsch',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': 'Die Mindestlänge der Mobiltelefonnummer beträgt 8 Ziffern',
    '邮箱账号名称最小长度为6位': 'Die Mindestlänge des E-Mail-Kontonamens beträgt 6 Zeichen',
    '邮箱只能包含英文，数字等字符': 'Die Mailbox darf nur Zeichen wie Englisch und Zahlen enthalten',
    '请选择正确的收货地址': 'Bitte wählen Sie die richtige Lieferadresse',
    ...deLocale
}

export default de