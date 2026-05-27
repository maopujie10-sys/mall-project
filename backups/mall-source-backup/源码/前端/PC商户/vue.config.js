/*
 * @Author: your name
 * @Date: 2022-03-03 21:23:53
 * @LastEditTime: 2023-01-04 23:33:49
 * @LastEditors: Please set LastEditors
 * @Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 * @FilePath: \www-pro\vue.config.js
 */
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
const CompressionPlugin = require("compression-webpack-plugin");
const TITLE = process.env.VUE_APP_TITLE;

const path = require('path')

function resolve(dir) {
  return path.join(__dirname, './', dir)
}

module.exports = {
  productionSourceMap: false, //设为false,既可减少包大小，也可以加密源码
  //publicPath: '/pc/', //部署应用时的根路径(默认'/'),也可用相对路径(存在使用限制)
  // outputDir: 'dist', //运行时生成的生产环境构建文件的目录(默认'dist'，构建之前会被清除)
  // assetsDir: '', //静态资源目录(js、css、img、fonts)，相对outputDir的目录(默认'')
  // indexPath: 'index.html', //指定生成index.html的输出路径(相对outputDir)也可以是绝对路径
  // lintOnSave: true, //是否开启ESlint（保存时检查）
  // productionSourceMap: true, //生产环境是否生成 sourceMap 文件
  // pages: { //pages里配置的路径和文件名在你的文档目录必须存在，否则启动服务会报错
  // 	index: { //除了 entry 之外都是可选的
  // 		entry: 'src/index/main.js', //page的主入口
  // 		template: 'public/index.html', //模板来源
  // 		filename: 'index.html', //在 dist/index.html 的输出
  // 		//title在template中使用：<title><%=htmlWebpackPlugin.options.title%></title>
  // 		title: '生成的配置信息',
  // 		chunks: ['chunk-vendors', 'chunk-common', 'index']
  // 		// 在这个页面中包含的块，默认情况下会包含,提取出来的通用 chunk 和 vendor chunk
  // 	},
  // 	subpage: 'src/subpage/main.js'
  // 	//官方解释：当使用只有入口的字符串格式时，模板会被推导为public/subpage.html
  // 	//若找不到就回退到public/index.html，输出文件名会被推导为subpage.html
  // },
  // css: {
  // 	extract: true, //是否使用css分离插件 ExtractTextPlugin
  // 	sourceMap: false, //开启 CSS source maps
  // 	loaderOptions: {}, //css预设器配置项
  // 	modules: false //启用CSS modules for all css / pre-processor files.
  // },
  publicPath: process.env.NODE_ENV === 'production' ? '././' : '/',
  outputDir: process.env.VUE_APP_ITEM_NAME == 'Shopify' ? 'dist' : process.env.VUE_APP_ITEM_NAME + ' - 用户商城PC',
  // outputDir: process.env.VUE_APP_ITEM_NAME == 'SM-wholesale shop' ? 'dist' : process.env.VUE_APP_ITEM_NAME + ' - 用户商城PC',
  chainWebpack: (config) => {
    config.plugin("html").tap((args) => {
      args[0].title = TITLE;
      args[0].version = new Date().toString();
      return args;
    }); 
    config.optimization.minimize(true); //压缩代码
    config.optimization.splitChunks({ chunks: "all" }); //分割代码
    // config.module
    //   .rule("image")
    //   .test(/\.(png|jpe?g|gif)(\?.*)?$/)
    //   .use("image-webpack-loader")
    //   .loader("image-webpack-loader")
    //   .options({
    //     // 此处为ture的时候不会启用压缩处理,目的是为了开发模式下调试速度更快
    //     disable: process.env.NODE_ENV === "development",
    //   })
    //   .end();
    config.module
      .rule('svg')
      .exclude.add(resolve('src/assets/icons'))
      .end();

    config.module
      .rule('icons')
      .test(/\.svg$/)
      .include.add(resolve('src/assets/icons'))
      .end()
      .use('svg-sprite-loader')
      .loader('svg-sprite-loader')
      .options({
        symbolId: '[name]'
      });
  },
  devServer: {
    //环境配置
    host: "localhost",
    port: 8080,
    https: false, //是否开启https
    hotOnly: true, //是否配置热更新
    open: true, //配置自动启动浏览器
    proxy: {
      //配置多个代理跨域(配置一个 proxy: 'http://localhost:4000')
      "/": {
        // target: process.env.VUE_APP_BASE_URL + 'wap/',
        target: "http://localhost:8800/wap",
        ws: true, //是否跨域
        changeOrigin: true,
        // pathRewrite: {
        // 	'^/api': ''
        // }
      },
      // '/': {
      // 	target:'https://hajhiug.com/',
      // 	ws: true, //是否跨域
      // 	changeOrigin: true,
      // }
    },
  },
  configureWebpack: (config) => {
    if (process.env.NODE_ENV === "production") {
      // 为生产环境修改配置
      config.plugins.push(
        new UglifyJsPlugin({
          uglifyOptions: {
            compress: {
              drop_debugger: true,
              drop_console: true, //生产环境自动删除console
            },
            warnings: false,
          },
          sourceMap: false,
          parallel: true, //使用多进程并行运行来提高构建速度。默认并发运行数：os.cpus().length - 1。
        }),
        new CompressionPlugin({
          test: /\.js$|\.html$|\.css$|\.jpg$|\.jpeg$|\.png/, // 需要压缩的文件类型
          threshold: 10240, // 归档需要进行压缩的文件大小最小值，我这个是10K以上的进行压缩
          deleteOriginalAssets: false, // 是否删除原文件
          minRatio: 0.8,
        })
      );
    }

    // pluginOptions: { // 第三方插件配置
    // 	// ...
    // }
  },
};
