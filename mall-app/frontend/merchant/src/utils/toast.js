import {Loading, Notification} from 'element-ui'
import {i18n} from '@/lang'

let loading = null
let notification = null

const Toast = (options) => {
    notification = Notification.info({
        title: i18n.t('提示'),
        message: options
    })
}


Toast.success = (options) => {
    notification = Notification.success({
        title: i18n.t('成功'),
        message: options
    })
}

Toast.fail = (options) => {
    notification = Notification.error({
        title: i18n.t('错误'),
        message: options
    })
}

Toast.clear = () => {
    notification && notification.close()
    loading && loading.close()
}

Toast.loading = () => {
    loading = Loading.service()
}
export default Toast
