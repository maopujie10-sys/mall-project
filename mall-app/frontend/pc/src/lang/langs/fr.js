import frLocale from 'element-ui/lib/locale/lang/fr'
import home from './fr/home'

const fr = {
    language: 'français',
    message: {
        'home': home,
    },
    '手机号码最小长度为8位': 'La longueur minimale du numéro de téléphone mobile est de 8 chiffres',
    '邮箱账号名称最小长度为6位': 'La longueur minimale du nom du compte de messagerie est de 6 caractères',
    '邮箱只能包含英文，数字等字符': "La boîte aux lettres ne peut contenir que des caractères tels que l'anglais et des chiffres",
    '请选择正确的收货地址': 'Veuillez sélectionner la bonne adresse de livraison',
    ...frLocale
}
export default fr
