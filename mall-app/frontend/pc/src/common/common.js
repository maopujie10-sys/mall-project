/*
 * @Author: your name
 * @Date: 2022-03-23 22:42:20
 * @LastEditTime: 2022-03-24 00:03:44
 * @LastEditors: Please set LastEditors
 * @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 * @FilePath: \www-pro\src\common\common.js
 */

export function strFirstBit(val){
    let arr=val.map((val,index,arr) => {
       return val.currency
    });
    return arr
}
export function filterArrayEmpty(val){
    let isEmpty=val.every(val=>{
        return val!=''
    })
    return isEmpty
}
export class WhrWebSocket {
    constructor(params) {
    	//只有params这个参数必须卸载constructor方法里，其他的实例属性可以写在外面
    	// 比如 socket = null
        this.socket = null
        this.params = params
        this.j = 0 //websocket重连次数
        this.i = 0//发送信息次数
    }

    init(params) {
        if (this.params.path) {
            this.path = this.params.path
        } else {
            throw new Error('参数socket服务器地址path必须存在')
        }

        this.socket = new WebSocket(this.path)
        this.socket.onopen = () => {
            
            console.log("连接开启")
        }
        // this.socket.onclose = () => {
         
        //     console.log("连接关闭")
        //     this.reconnect()
        // }
        // this.socket.onerror = () => {
        //     console.log("连接错误")
        // }
        this.socket.onmessage =this.params.onmessage


    }

    // getMessage(msg) {
    //     console.log("收到的消息", msg)
    //     return msg
    // }

	close() {
        clearTimeout(this.time)
        this.socket.close(1000, '手动关闭')
    }
  
}
