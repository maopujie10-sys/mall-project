import afLocale from 'element-ui/lib/locale/lang/af-ZA'
import home from './af/home'

const af = {
    language: 'Afrikaans',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': 'Die minimum lengte van die selfoonnommer is 8 syfers',
    '邮箱账号名称最小长度为6位': 'Die minimum lengte van die e-posrekeningnaam is 6 karakters',
    '邮箱只能包含英文，数字等字符': 'Die posbus kan slegs karakters soos Engels en nommers bevat',
    '请选择正确的收货地址': 'Kies asseblief die korrekte afleweringsadres',
    ...afLocale
}
export default af