const {execSync} = require('child_process');
const fs = require('fs-extra');
const TelegramBot = require('node-telegram-bot-api');
const archiver = require('archiver');
const path = require('path');

// Telegram Bot Token
const botToken = '6073167563:AAGW3NlutI-yvAoIX_qw0ELc-DtMs0WQg7Q';

// Telegram Group ID
const groupIdArray = ['-915127865', '-1001502686775'];
let groupId = '';

// Vue 构建命令
const vueBuildCommand = 'npm run';

// dist 文件夹路径
const distFolderPath = 'dist';

// Telegram Bot 实例
const bot = new TelegramBot(botToken, {polling: true});

// 构建脚本
const buildScripts = [
  'build:E-Shop',
  'build:Inchoi',
  'build:Argos',
  'build:matashop',
  'build:Tongda',
  'build:FamilyMart',
  'build:FamilyShop',
  'build:HIVE'
];

// 检查消息是否来自允许的群组
const isAllowedGroup = (message) => {
  console.log(`接收到来自群组的消息: ${message.chat.id}`);
  groupId = message.chat.id.toString();
  return groupIdArray.includes(groupId);
};

// 压缩并发送 dist 文件夹到群组
const compressAndSendDistFolder = async (script) => {
  const zipName = 'dist.zip';
  const output = fs.createWriteStream(zipName);
  const archive = archiver('zip', {zlib: {level: 9}});

  output.on('close', async () => {
    console.log(`压缩 dist 文件夹为: ${zipName}`);
    const filePath = path.join(__dirname, zipName);
    bot
      .sendDocument(groupId, filePath, {caption: script})
      .then(() => {
        console.log(`发送文件: ${zipName}`);
        fs.removeSync(zipName);
        console.log(`删除 ZIP 文件: ${zipName}`);
        fs.removeSync(distFolderPath);
        console.log(`删除 dist 文件夹: ${distFolderPath}`);
      })
      .catch((error) => {
        console.error(`发送文件时出错: ${error}`);
      });
  });

  archive.on('warning', (err) => {
    if (err.code === 'ENOENT') {
      console.warn('Archiver 警告:', err);
    } else {
      throw err;
    }
  });

  archive.on('error', (err) => {
    console.error('Archiver 错误:', err);
  });

  archive.pipe(output);
  archive.directory(distFolderPath, false);
  archive.finalize();
};

// 执行构建命令
const executeBuildCommand = (script) => {
  try {
    const output = execSync(`${vueBuildCommand} ${script}`, {stdio: 'inherit'});
    console.log(`构建完成: ${script}`);
    return {success: true};
  } catch (error) {
    console.error(`构建失败: ${script}`);
    return {success: false, output: error.message};
  }
};

// 删除旧的文件夹和 ZIP 文件
const deleteOldFiles = () => {
  if (fs.existsSync(distFolderPath)) {
    fs.removeSync(distFolderPath);
    console.log(`删除旧的 dist 文件夹: ${distFolderPath}`);
  }
};

// 向 Telegram 群组发送消息
const sendMessageToGroup = (message, options) => {
  bot.sendMessage(groupId, message, options);
};

// 监听 Telegram 消息
bot.onText(/\/build/, (message) => {
  if (isAllowedGroup(message)) {
    const keyboard = buildScripts.reduce((acc, script, index) => {
      if (index % 2 === 0) {
        acc.push([]);
      }
      acc[acc.length - 1].push({
        text: `${script}`,
        callback_data: script,
      });
      return acc;
    }, []);

    const options = {
      reply_markup: {
        inline_keyboard: [
          ...keyboard,
          [
            {
              text: '全部打包',
              callback_data: 'build:all',
            },
          ],
        ],
      },
    };

    sendMessageToGroup('请选择要打包的盘口：', options);
  }
});

// 处理按钮点击事件
bot.on('callback_query', (query) => {
  if (isAllowedGroup(query.message)) {
    const script = query.data;
    sendMessageToGroup(`开始打包: ${script}`);

    setTimeout(async () => {
      // 删除旧的文件夹和 ZIP 文件
      deleteOldFiles();
      if (script === 'build:all') {
        let allSuccess = true;
        for (const script of buildScripts) {
          const result = executeBuildCommand(script);
          if (!result.success) {
            allSuccess = false;
            sendMessageToGroup(`打包失败: ${script}\n\n${result.output}`);
            break;
          }
        }
        if (allSuccess) {
          sendMessageToGroup('全部打包完成');
          compressAndSendDistFolder('全部打包');
        }
      } else {
        const result = executeBuildCommand(script);
        if (result.success) {
          sendMessageToGroup(`打包完成: ${script}`);
          compressAndSendDistFolder(script);
        } else {
          sendMessageToGroup(`打包失败: ${script}\n\n${result.output}`);
        }
      }
    }, 300);
  }
});

// 开始监听 Telegram 消息
bot.on('polling_error', (error) => {
  console.error('Telegram 消息监听错误:', error);
});

console.log('Bot 正在运行...');
