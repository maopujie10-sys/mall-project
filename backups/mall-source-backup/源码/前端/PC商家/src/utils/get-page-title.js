import defaultSettings from '@/settings'

const title = (defaultSettings.siteTitle || defaultSettings.projectTitle) || 'Vue Admin Template'

const {i18n} = require('@/lang')

export default function getPageTitle(pageTitle) {
    if (pageTitle) {
        let str = `${i18n.t(pageTitle)} - ${title}`
        return str
    }
    return `${title}`
}
