import esLocale from 'element-ui/lib/locale/lang/es'
import home from './es/home'

const es = {
    language: 'Español',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': 'La longitud mínima del número de teléfono móvil es de 8 dígitos',
    '邮箱账号名称最小长度为6位': 'La longitud mínima del nombre de la cuenta de correo electrónico es de 6 caracteres',
    '邮箱只能包含英文，数字等字符': 'El buzón solo puede contener caracteres como inglés y números',
    '请选择正确的收货地址': 'Seleccione la dirección de envío correcta',
    ...esLocale
}

export default es
