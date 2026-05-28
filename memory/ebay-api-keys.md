# eBay API 密钥配置说明

> ⚠️ 真实密钥存储在 .env 文件中，切勿提交到 Git

## 配置方式
在 .env 文件中添加以下环境变量：

\\\
EBAY_SANDBOX_APP_ID=你的Sandbox App ID
EBAY_SANDBOX_CERT_ID=你的Sandbox Cert ID
EBAY_PRODUCTION_APP_ID=你的Production App ID
EBAY_PRODUCTION_CERT_ID=你的Production Cert ID
EBAY_DEV_ID=你的Developer ID
\\\

## API 端点
- Finding API: https://svcs.ebay.com/services/search/FindingService/v1
- Shopping API: https://open.api.ebay.com/shopping

## 获取密钥
1. 注册 eBay Developers Program: https://developer.ebay.com
2. 创建应用获取 Sandbox 密钥（免费测试）
3. 通过审核后获取 Production 密钥
