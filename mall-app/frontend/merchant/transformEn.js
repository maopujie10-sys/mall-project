const fs = require('fs')
const path = require('path')
const translate = require('@plainheart/google-translate-api');
const lang = require('./src/lang/en');
// 引入 node-xlsx 模块
const xlsx = require('node-xlsx');

// excel文件类径
const excelFilePath = '商城国际化翻译文档4.xlsx'
//解析excel, 获取到所有sheets
const sheets = xlsx.parse(excelFilePath);

let langEn = {}
sheets.forEach((sheet) => {
  if (sheet.name === '商家PC') {
    // 读取excel中的数据
    const data = sheet.data;
    // 遍历数据
    data.forEach((item, index) => {
      // 第一行是标题，不需要
      if (index !== 0) {
        // 获取到key
        const key = item[0];
        // 获取到翻译后的value
        const value = item[2];
        // 将翻译后的value写入到langEn中
        langEn[key] = value;
      }
    });
  }
})

let allStrArray = [];
let languageArray = [
  {name: '繁體中文', fileName: 'zh-TW', code: 'zh-TW'},
  {name: '简体中文', fileName: 'zh-CN', code: 'zh-CN'},
  {name: 'English', fileName: 'en', code: 'en'},
  {name: 'Deutsch', fileName: 'de', code: 'de'},
  {name: 'Français', fileName: 'fr', code: 'fr'},
  {name: '日本語', fileName: 'ja', code: 'ja'},
  {name: '한국어', fileName: 'ko', code: 'ko'},
  {name: 'Melayu', fileName: 'ms', code: 'ms'},
  {name: 'ภาษาไทย', fileName: 'th', code: 'th'},
  {name: 'Português', fileName: 'pt', code: 'pt'},
  {name: 'Español', fileName: 'es', code: 'es'},
  {name: 'Русский', fileName: 'ru', code: 'ru'},
  {name: 'Ελληνικά', fileName: 'el', code: 'el'},
  {name: 'Italiano', fileName: 'it', code: 'it'},
  {name: 'Türkçe', fileName: 'tr-TR', code: 'tr'},
  {name: 'Afrikaans', fileName: 'af-ZA', code: 'af'},
  {name: 'Filipino', value: 'tl', code: 'tl', show: true}, // 菲律宾语
  {name: 'العربية', value: 'ar', code: 'ar', show: true}, // 阿拉伯语
  {name: 'Tiếng Việt', value: 'vi', code: 'vi', show: true}, // 越南语
  {name: 'हिंदी', value: 'hi', code: 'hi', show: true}, // 印地语
  {name: 'bahasa Indonesia', value: 'id', code: 'id', show: true}, // 印尼语
]
let newPath = "srcCopy" //新目录地址
let langPath = "lang" //语言包地址，创建在newPath目录下

for (let i in lang) {
  allStrArray.push({key: i, value: lang[i], translate: ''});
}

allStrArray = [...new Set(allStrArray)].sort()

let translateCodeIndex = 0
const translateCodeFunc = () => {
  if (languageArray.length > translateCodeIndex) {
    translateCode(languageArray[translateCodeIndex]).then(res => {

      translateCodeIndex++
      translateCodeFunc()
    })
  }
}

//翻译代码
function translateCode(language) {
  return new Promise((resolve, reject) => {
    // 如果allStrArray长度大于100 分成数组
    let allStrArrayLength = allStrArray.length
    let allStrArrayLengthArray = []
    let translateArray = []
    let allStrArrayLengthArrayIndex = 0
    for (let i = 0; i < allStrArrayLength; i++) {
      if (i % 100 === 0) {
        allStrArrayLengthArray[allStrArrayLengthArrayIndex] = []
        allStrArrayLengthArrayIndex++
      }
      allStrArrayLengthArray[allStrArrayLengthArrayIndex - 1].push(allStrArray[i])
    }
    //递归翻译
    let funcIndex = 0
    const translateFunc = () => {
      if (funcIndex < allStrArrayLengthArray.length) {
        let arrayObj = allStrArrayLengthArray[funcIndex]
        let item = []
        arrayObj.forEach(itemObj => {
          item.push(itemObj.value)
        })
        let str = item.join('\n')
        console.log(language.code + '内容翻译中... ' + (funcIndex + 1) + '/' + allStrArrayLengthArray.length)
        translate(str, {to: language.code}).then(res => {
          let arr = res.text.split('\n')
          // 去掉数组元素的前后空格
          arr.forEach((item, index) => {
            translateArray.push({key: arrayObj[index].key, value: arrayObj[index].value, translate: item.trim()})
          })

          if (funcIndex >= allStrArrayLengthArray.length - 1) {
            // 将中文和翻译后的英文写入到json文件中
            let newArr = []
            let obj = {}
            allStrArray.forEach((item, index) => {
              newArr.push({key: item.key, value: item.value, translate: translateArray[index].translate})
              // obj[item.key] = translateArray[index].translate
            })
            newArr.sort((a, b) => {
              // 使用unicode编码排序
              return a.key.localeCompare(b.key, 'zh-Hans-CN-u-co-pinyin')
            })
            newArr.forEach(item => {
              obj[item.key] = item.translate
            })
            if (language.code === 'en') {
              for (let i in langEn) {
                if (langEn[i]) {
                  obj[i] = langEn[i]
                }
              }
            }
            const myPath = path.relative(__dirname, path.join(__dirname, newPath, langPath, `${language.fileName}.js`))
            _deleteDir(myPath, () => {
              writeFileByUser(myPath, `${language.fileName}.js`, `module.exports = ` + JSON.stringify(obj))
            })
            resolve(`翻译完成：${language.code}`)
          } else {
            funcIndex++
            translateFunc()
          }
        }).catch(err => {
          console.error(err)
          reject(err)
        })
      }
    }
    translateFunc()
  })
}


//写文件
function writeFileByUser(filePath, fileName, data) {
  let myPath = filePath.replace(`\\${fileName}`, '')
  myPath = filePath.replace(`\/${fileName}`, '')
  if (fs.existsSync(filePath)) {
  } else {
    let err = fs.mkdirSync(path.join(__dirname, myPath), {recursive: true})
    if (err) {
      console.log(err)
    } else {
      console.log('创建目录成功:', myPath)
    }
    fs.writeFileSync(path.join(__dirname, filePath), data, 'utf-8', function (err) {
      if (err) {
        console.log(err);
      } else {
        console.log(`写入文件: \x1B[32m${path.join(__dirname, myPath, fileName)}`)
      }
    })
  }
}

const _deleteDir = (directoryPath, callback) => {
  const fs = require('fs').promises;

  async function rmdirAsync(directoryPath) {
    try {
      let stat = await fs.stat(directoryPath)
      if (stat.isFile()) {
        await fs.unlink(directoryPath)
      } else {
        let dirs = await fs.readdir(directoryPath)
        // 递归删除文件夹内容(文件/文件夹)
        dirs = dirs.map(dir => rmdirAsync(path.join(directoryPath, dir)))
        await Promise.all(dirs)
        await fs.rmdir(directoryPath)
      }
    } catch (e) {
      console.error(e);
    }
  }

  if (require('fs').existsSync(directoryPath)) {
    rmdirAsync(directoryPath).then(() => {
      // 确保文件/文件夹均已删除 => 回调
      console.log('删除目录成功:', directoryPath)
      callback && callback();
    })
  } else {
    callback && callback();
  }
}

translateCodeFunc()
