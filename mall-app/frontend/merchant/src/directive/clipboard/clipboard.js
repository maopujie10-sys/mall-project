// 参考 https://github.com/Inndy/vue-clipboard2
import Clipboard from 'clipboard'

if (!Clipboard) {
    throw new Error('请先使用 npm install clipboard --save 安装 `clipboard` 包')
}

function bindClipboard(el, binding) {
    if (binding.arg === 'success') {
        el._v_clipboard_success = binding.value
    } else if (binding.arg === 'error') {
        el._v_clipboard_error = binding.value
    } else {
        el._v_clipboard = new Clipboard(el, {
            text() {
                return binding.value
            },
            action() {
                return binding.arg === 'cut' ? 'cut' : 'copy'
            }
        })

        el._v_clipboard.on('success', e => {
            const callback = el._v_clipboard_success
            callback && callback(e)
        })

        el._v_clipboard.on('error', e => {
            const callback = el._v_clipboard_error
            callback && callback(e)
        })
    }
}

function updateClipboard(el, binding) {
    if (binding.arg === 'success') {
        el._v_clipboard_success = binding.value
    } else if (binding.arg === 'error') {
        el._v_clipboard_error = binding.value
    } else {
        el._v_clipboard.text = function () {
            return binding.value
        }
        el._v_clipboard.action = function () {
            return binding.arg === 'cut' ? 'cut' : 'copy'
        }
    }
}

function unbindClipboard(el, binding) {
    if (binding.arg === 'success') {
        delete el._v_clipboard_success
    } else if (binding.arg === 'error') {
        delete el._v_clipboard_error
    } else {
        el._v_clipboard.destroy()
        delete el._v_clipboard
    }
}

export default {
    bind: bindClipboard,
    update: updateClipboard,
    unbind: unbindClipboard
}
