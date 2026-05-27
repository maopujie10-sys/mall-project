const fs = require('fs');
const translate = require('@plainheart/google-translate-api');
const ProgressBar = require('progress');

// 读取英文翻译数据
const enData = require('./src/lang/en.js');

// 定义需要生成的其他语言列表
const languages = [
  { name: '繁體中文', fileName: 'zh-TW', code: 'zh-TW' },
  { name: '简体中文', fileName: 'zh-CN', code: 'zh-CN' },
  { name: 'English', fileName: 'en', code: 'en' },
  { name: 'Deutsch', fileName: 'de', code: 'de' },
  { name: 'Français', fileName: 'fr', code: 'fr' },
  { name: '日本語', fileName: 'ja', code: 'ja' },
  { name: '한국어', fileName: 'ko', code: 'ko' },
  { name: 'Melayu', fileName: 'ms', code: 'ms' },
  { name: 'ภาษาไทย', fileName: 'th', code: 'th' },
  { name: 'Português', fileName: 'pt', code: 'pt' },
  { name: 'Español', fileName: 'es', code: 'es' },
  { name: 'Русский', fileName: 'ru', code: 'ru' },
  { name: 'Ελληνικά', fileName: 'el', code: 'el' },
  { name: 'Italiano', fileName: 'it', code: 'it' },
  { name: 'Türkçe', fileName: 'tr-TR', code: 'tr' },
  { name: 'Afrikaans', fileName: 'af-ZA', code: 'af' },
  { name: 'Filipino', value: 'tl', fileName: 'tl', code: 'tl', show: true }, // 菲律宾语
  { name: 'العربية', value: 'ar', fileName: 'ar', code: 'ar', show: true }, // 阿拉伯语
  { name: 'Tiếng Việt', value: 'vi', fileName: 'vi', code: 'vi', show: true }, // 越南语
  { name: 'हिंदी', value: 'hi', fileName: 'hi', code: 'hi', show: true }, // 印地语
  { name: 'bahasa Indonesia', value: 'id', fileName: 'id', code: 'id', show: true }, // 印尼语
];

// 用于存储生成的语言翻译数据
const languageData = {};

// 异步函数，用于生成指定语言的翻译数据
async function generateLanguageData(language) {
  const translations = {};
  const totalKeys = Object.keys(enData).length;
  let translatedKeys = 0;

  console.log(`开始生成 ${language.name} (${language.code}) 语言翻译数据`);

  for (const key in enData) {
    const translation = await translate(enData[key], { to: language.code });
    translations[key] = translation.text;
    translatedKeys++;

    // 打印翻译进度
    const progress = (translatedKeys / totalKeys) * 100;
    console.log(`[${language.name} (${language.code})] 翻译进度: ${progress.toFixed(2)}%`);
  }

  console.log(`生成 ${language.name} (${language.code}) 语言翻译数据完成`);
  languageData[language.fileName] = translations;
}

async function generateAllLanguages() {
  const promises = languages.map(language => generateLanguageData(language));
  await Promise.all(promises);

  for (const language of languages) {
    const filePath = `./src/lang/${language.fileName}.js`;
    const fileContent = `module.exports = ${JSON.stringify(languageData[language.fileName], null, 2)};\n`;

    fs.writeFile(filePath, fileContent, (err) => {
      if (err) {
        console.error(`写入文件 ${filePath} 失败: ${err}`);
      } else {
        console.log(`写入文件 ${filePath} 成功`);
      }
    });
  }
}

generateAllLanguages();
