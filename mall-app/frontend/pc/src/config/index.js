
// let env_url = 'thsjbvh.site'
let env_url = 'localhost:8800'
const pro_url = window.location.hostname

let ENV_DEV = 'http://' + env_url+'/wap/' // dev
let ENV_PRO = 'https://' + pro_url + '/wap/' 


let HOST_URL =''
let BASE_URL = ''
let WS_URL = ''
if (process.env.NODE_ENV === "development"){
    HOST_URL = 'http://' + env_url
    BASE_URL = ENV_DEV
    WS_URL = `wss://${env_url}/data/websocket`
}else{
    HOST_URL = 'https://' + pro_url
    BASE_URL =  ENV_PRO
    WS_URL = `ws://localhost/data/websocket` // 演示环境
}


export default {
    HOST_URL,
    BASE_URL,
    WS_URL,
}
