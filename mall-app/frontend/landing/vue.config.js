const { defineConfig } = require('@vue/cli-service')
const NodePolyfillPlugin = require('node-polyfill-webpack-plugin');
module.exports = defineConfig({
    transpileDependencies: true,
    lintOnSave: false,
    productionSourceMap: false,
    configureWebpack: {
        plugins: [new NodePolyfillPlugin()],
        module: {
            rules: [
            ]
        }
    },
    publicPath: '/promote/',
    outputDir: process.env.VUE_APP_ITEM_NAME == 'Sky City' ? 'dist' : process.env.VUE_APP_ITEM_NAME + ' - ldy',
    // outputDir: process.env.VUE_APP_ITEM_NAME == 'TikTok-Wholesale' ? 'dist' : process.env.VUE_APP_ITEM_NAME + ' - ldy',
    assetsDir: 'assets',
    devServer: {
        port: 8090,
        host: '127.0.0.1',
        https: false,
        proxy: {
            // 可为不同的接口配置不同的代理地址
            '/wap/api': {
                // 服务地址，即你要访问的服务器地址
                // target: 'https://rfbhabkjk.com/wap/',
                target: 'http://localhost:8800/wap/',
                // 路径重写，将'/user/login'重写为'/login'
                pathRewrite: {
                    '^/wap/api': ''
                },
                // 所有信息都在命令行工具打印
                logLevel: 'debug'
            },
        }
    }
})
