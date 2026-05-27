const fs = require('fs')
const path = require('path')
const $ = require('gogocode');
const translate = require('@plainheart/google-translate-api');
const langZH = require('./src/lang/zh-CN')
const country = require('./src/utils/country')

//读取src文件夹下的所有文件转成文件流
const readDir = (dir) => {
  const files = fs.readdirSync(dir)
  return files.map(file => {
    const filePath = path.join(dir, file)
    const stat = fs.statSync(filePath)
    if (stat.isDirectory()) {
      return readDir(filePath)
    } else {
      //返回当前文件的文件流
      try {
        return fileTranslate(fs.readFileSync(filePath, 'utf-8'), file, filePath)
      } catch (err) {
        console.log(err)
      }
    }
  })
}

const rule = (ast, options) => {
  // 你的转换逻辑

  return ast
}
let labelAttributeArray = [] //存储标签中所有的中文属性
let contentArray = []   //存储标签中夹着的中文
let mixedWithChineseArray = [] //存储标签中夹着的不被标签包裹的中文

const findAllChinese = (text) => {
  text = typeof text === 'string' ? text.trim() : text
  const code = (text + '').replace(/\r\n/g, "")
  let reg = new RegExp("[\\u4E00-\\u9FFF]+", "g")
  if (/^[\/\\、%&'，,;：:=?\x22\u4e00-\u9fa5_a-zA-Z0-9]+$/.test(code) && reg.test(code)) {
    return true
  } else {
    return false
  }
}

// 文件内容转译
const fileTranslate = (file, fileName, filePath) => {
  if (file) {
    labelAttributeArray = [] //存储标签中所有的中文属性
    contentArray = []   //存储标签中夹着的中文
    mixedWithChineseArray = [] //存储标签中夹着的不被标签包裹的中文
    let scriptCodeArray = []

    let otherStrArray = []
    const code = file//.replace(/[\r\n]/g, "")
    const input = $(code, {parseOptions: {language: 'vue'}});
    /**
     * 获取javascript的代码块中的中文
     * @type {*|jQuery}
     */
      // 获取javascript的代码块
    let scriptCode = $(input, {
        parseOptions: {
          language: 'vue'
        }
      }).find('<script></script>')
    // 获取javascript中，冒号后面的中文
    scriptCode.find(`$_$0:$_$1`).each((match, index) => {
      let attribute = match[0].match[1][0].value
      if (findAllChinese(attribute)) {
        scriptCodeArray.push({str: attribute})
        match.replace(`$_$:$$$`, `$_$:this.$t('${attribute}')`)
      }
    })
    scriptCodeArray.forEach((item, index) => {
      allStrArray.push((item.str + '').trim())
      //scriptCode.replace(`$_$0:${item.str}`, `$_$0:this.$t('${(item.str + '').trim()}')`)
    })
    // 获取javascript中，等号后面的中文
    scriptCodeArray = []
    scriptCode.find(`let $_$0 = $_$1`).each((match, index) => {
      let attribute = match[0].match[1][0].value
      if (findAllChinese(attribute)) {
        scriptCodeArray.push({str: attribute})
        match.replace(`let $_$0 = $_$1`, `let ${match[0].match[0][0].value} = this.$t('${attribute}')`)
      }
    })
    scriptCode.find(`const $_$0 = $_$1`).each((match, index) => {
      let attribute = match[0].match[1][0].value
      if (findAllChinese(attribute)) {
        scriptCodeArray.push({str: attribute})
        match.replace(`const $_$0 = $_$1`, `const ${match[0].match[0][0].value} = this.$t('${attribute}')`)
      }
    })

    scriptCode.find(`$_$0 += $_$1`).each((match, index) => {
      let attribute = match[0].match[1][0].value
      if (findAllChinese(attribute)) {
        scriptCodeArray.push({str: attribute})
        match.replace(`$_$0 += $_$1`, `${match[0].match[0][0].value} = this.$t('${attribute}')`)
      }
    })

    scriptCode.find(`$$$.$t($_$0)`).each((match, index) => {
      let attribute = match[0].match[0][0].value
      if (findAllChinese(attribute)) {
        scriptCodeArray.push({str: attribute})
      }
    })
    scriptCodeArray.forEach((item, index) => {
      allStrArray.push((item.str + '').trim())
    })

    /**
     * 获取vue文件中标签中的中文
     * @type {*|jQuery}
     */
    // 获取标签属性中的中文
    scriptCode.root().find('<template></template>').find('<$_$1 $_$2="$_$3" $$$0></$_$1>').each((match, index) => {
      let attribute = match[0].match[3]
      attribute.forEach((item, index) => {
        if (findAllChinese(item.value)) {
          labelAttributeArray.push({
            tag: match[0].match[1][0].value,
            attribute: match[0].match[2][index].value,
            str: item.value,
            attributeNumber: match[0].match[2].length
          })
        } else if (item.value?.indexOf('$t(') >= 0) {
          otherStrArray.push({str: item.value.replace('$t(', '').replace(')', '').replace(/'/g, '').replace(/"/g, '').replace(/`/g, '')})
        }
      })
    })
    labelAttributeArray.forEach(item => {
      allStrArray.push((item.str + '').trim())
      if (item.attributeNumber > 1) {
        scriptCode.root().find('<template></template>').replace(`<${item.tag} ${item.attribute}="${item.str}" $$$0>$$$1</${item.tag}>`, `<${item.tag} :${item.attribute}="$t('${(item.str + '').trim()}')" $$$0>$$$1</${item.tag}>`)
      } else {
        scriptCode.root().find('<template></template>').replace(`<${item.tag} $_$1="${item.str}" $$$1>$$$2</${item.tag}>`, `<${item.tag} :$_$1="$t('${(item.str + '').trim()}')" $$$1>$$$2</${item.tag}>`)
      }
    })

    // 获取标签中夹杂的头尾是中文的内容 <div>中文1<span>中文2</span>中文3</div>
    scriptCode.root().find('<template></template>').find(`<$_$1>$_$2</$_$3>`).each((match, index) => {
      let attribute = match[0].match[2][0].value
      //去掉attribute中的所有换行
      attribute = attribute.replace(/[\r\n]/g, "").trim()
      let str = attribute.replace(/[^\u4e00-\u9fa5_a-zA-Z0-9]/gi, "\n")
      if (str[0] !== "\n" && str.indexOf("\n") !== -1) {
        //去掉字符串中第一个*之后的字符串
        str = str.slice(0, str.indexOf("\n"))
        if (str.length > 0) {
          mixedWithChineseArray.push({str, tail: attribute.slice(str.length)})
        }
      } else if (attribute?.indexOf('$t(') >= 0 && attribute?.indexOf('</') === -1) {
        let obj = {str: attribute.replace('{{', '').replace('}}', '').replace('$t(', '').replace(')', '').replace(/'/g, '').replace(/"/g, '').replace(/`/g, '').replace(/:/g, '').trim()}
        if (findAllChinese(obj.str)) {
          otherStrArray.push(obj)
        }
      }
    })

    mixedWithChineseArray.forEach(item => {
      if (item.tail) {
        allStrArray.push((item.str + '').trim())
        scriptCode.root().find('<template></template>').replace(`<$_$1 $$$>${item.str}${item.tail}</$_$3>`, `<$_$1 $$$>{{$t('${(item.str + '').trim()}')}}${item.tail.replace(/[\r\n]/g, "")}</$_$3>`)
      }
    })

    scriptCode.root().find('<template></template>').find(`<$_$1>$_$2</$_$3>`).each((match, index) => {
      let attribute = match[0].match[2][0].value
      attribute = attribute.replace(/[\r\n]/g, "").trim()
      //判断字符串首尾不为*，则为中文
      let tailStr = attribute.replace(/[^\u4e00-\u9fa5_a-zA-Z0-9]/gi, "\n")
      // 判断字符串首尾不为*，则为中文
      if (tailStr[tailStr.length - 1] !== "\n" && tailStr.indexOf("\n") !== -1) {
        tailStr = tailStr.slice(tailStr.lastIndexOf("\n") + 1)
        mixedWithChineseArray.push({
          str: tailStr, head: attribute.slice(0, tailStr.lastIndexOf("\n") - tailStr.length)
        })
      }
    })

    mixedWithChineseArray.forEach(item => {
      if (item.head) {
        allStrArray.push((item.str + '').trim())
        scriptCode.root().find('<template></template>').replace(`<$_$1 $$$>${item.head} ${item.str}</$_$3>`, `<$_$1 $$$>${item.head.replace(/[\r\n]/g, "")}{{$t('${(item.str + '').trim()}')}}</$_$3>`)
      }
    })

    // 获取标签中全是中文的内容
    scriptCode.root().find('<template></template>').find(`<$_$1 $$$>$_$2</$_$3>`).each((match, index) => {
      let attribute = match[0].match[2][0].value
      if (findAllChinese(attribute)) {
        contentArray.push({str: attribute})
      }
    })
    contentArray.forEach(item => {
      allStrArray.push((item.str + '').trim())
      scriptCode.root().find('<template></template>').replace(`<$_$1 $$$>${item.str}</$_$3>`, `<$_$1 $$$>{{$t('${(item.str + '').trim()}')}}</$_$3>`)
    })

    otherStrArray.forEach(item => {
      allStrArray.push((item.str + '').trim())
    })
    // console.log(otherStrArray)
    let outputCode = scriptCode.root().generate()
    //去掉outputCode中的所有换行符
    // outputCode = outputCode.replace(/[\r\n]/g, "")
    //获取文件路径filePath相对于__dirname的位置
    let relativePath = path.relative(__dirname, filePath)
    //写文件 如果目录不存在 则新建目录
    writeFileByUser(relativePath.replace('src', newPath), fileName, fileName.lastIndexOf('.vue') > -1 ? outputCode : file)
    allStrArray = [...new Set(allStrArray)]
  }
}

const deleteHeaderTailStr = (str, location = false) => {
  if (location ? str.indexOf("\n") === 0 : str.lastIndexOf("\n") === 0) {
    deleteHeaderTailStr("\n", '')
  } else {
    return str
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
        let item = allStrArrayLengthArray[funcIndex]
        let str = item.join('\n')
        console.log(language + '内容翻译中... ' + (funcIndex + 1) + '/' + allStrArrayLengthArray.length)
        translate(str, {to: language}).then(res => {
          let arr = res.text.split('\n')
          // 去掉数组元素的前后空格
          arr.forEach((item, index) => {
            translateArray.push(item.trim())
          })
          if (funcIndex >= allStrArrayLengthArray.length - 1) {
            // 将中文和翻译后的英文写入到json文件中
            let obj = {}
            allStrArray.forEach((item, index) => {
              obj[item] = translateArray[index]
            })
            const myPath = path.relative(__dirname, path.join(__dirname, newPath, langPath, `${language}.js`))
            _deleteDir(myPath, () => {
              writeFileByUser(myPath, `${language}.js`, `module.exports = ` + JSON.stringify(obj))
            })
            resolve(`翻译完成：${language}`)
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

/**
 * 执行文件 需要初始化的一些参数
 * @type {*[]}
 */
let allStrArray = []
let readPath = "./src" //需要转译的目录地址
let newPath = "srcCopy" //新目录地址
let langPath = "lang" //语言包地址，创建在newPath目录下
const main = async () => {
  let langIndexFile = fs.readFileSync(path.join(__dirname, "src", langPath, "index.js"), "utf-8")
  readDir(path.join(__dirname, readPath))
  //调用谷歌翻译api翻译数组中的中文
  let languageArray = ['en', "zh-CN", 'ko', "zh-TW"] //'ko', "zh-CN", "zh-TW"

  let translateCodeIndex = 0

  for (let i in langZH) {
    allStrArray.push(i)
  }
  for (let i in country) {
    allStrArray.push(country[i].zh)
  }
  // allStrArray 去重
  allStrArray = [...new Set(allStrArray)].sort()
  const translateCodeFunc = () => {
    if (languageArray.length > translateCodeIndex) {
      translateCode(languageArray[translateCodeIndex]).then(res => {

        translateCodeIndex++
        translateCodeFunc()
      })
    }
  }
  translateCodeFunc()
}

_deleteDir(path.join(__dirname, newPath), () => {
  main()
})

