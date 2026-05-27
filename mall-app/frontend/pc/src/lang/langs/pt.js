import ptLocale from 'element-ui/lib/locale/lang/pt'
import home from './pt/home'

const pt = {
    language: 'Português',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': "O tamanho mínimo do número do celular é de 8 dígitos",
    '邮箱账号名称最小长度为6位': "O comprimento mínimo do nome da conta de e-mail é de 6 caracteres",
    '邮箱只能包含英文，数字等字符': "A caixa de correio só pode conter caracteres como inglês e números",
    '请选择正确的收货地址': 'Por favor, selecione o endereço de entrega correto',
    ...ptLocale
}
export default pt
