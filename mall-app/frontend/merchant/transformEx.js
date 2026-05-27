const fs = require('fs')
const path = require('path')
const translate = require('@plainheart/google-translate-api');
const lang = require('./src/lang/zh-CN');
// 引入 node-xlsx 模块
const xlsx = require('node-xlsx');

const filePath1 = '商城国际化翻译文档1.xlsx'
const filePath2 = '商城国际化翻译文档2.xlsx'

//解析excel, 获取到所有sheets
const sheets1 = xlsx.parse(filePath1);
const sheets2 = xlsx.parse(filePath2);

let langObject = {
  langArray1: [],
  langArray2: []
}
let titleArray = []
const getLangArray = (sheets, langeType) => {

  sheets.forEach((sheet) => {
    let pageArray = []
    const data = sheet.data;
    // 遍历数据
    data.forEach((item, index) => {
      // 第一行是标题，不需要
      if (index !== 0 && (item[0] || item[1])) {
        // 获取到key
        const key = item[0] || '';
        const cn = (item[1] || '').replace(/[\r\n]/g, '');
        const tw = item[2] || '';
        const en = item[3] || '';
        const de = item[4] || '';
        const fr = item[5] || '';
        const ja = item[6] || '';
        const ko = item[7] || '';
        const ms = item[8] || '';
        const th = item[9] || '';
        const pt = item[10] || '';
        const es = item[11] || '';
        const ru = item[12] || '';
        const el = item[13] || '';
        const it = item[14] || '';
        const tr = item[15] || '';
        const af = item[16] || '';
        // 将翻译后的value写入到langEn中
        pageArray.push({key, 'zh-CN': cn, 'zh-TW': tw, en, de, fr, ja, ko, ms, th, pt, es, ru, el, it, tr, af});
      } else {
        titleArray = item
      }
    });
    langObject[langeType].push(pageArray)
  })
}
getLangArray(sheets1, "langArray1")
getLangArray(sheets2, "langArray2")

langObject.langArray1.forEach((sheetsItem1, sheetsIndex1) => {
  sheetsItem1.forEach((item1, index1) => {
    langObject.langArray2[sheetsIndex1].forEach((item2, index2) => {
      if (item1['zh-CN'] === item2['zh-CN'] && item1.en) {
        item2.en = item1.en
      }
    })
    langObject.langArray2[sheetsIndex1].sort((a, b) => {
      // 按照Unicode码排序
      return a['zh-CN'].localeCompare(b['zh-CN'], 'zh-Hans-CN-u-co-pinyin')
    })
  })
})
const langArray = langObject.langArray2
let languageArray = [
  {name: 'English', value: 'en', code: 'en', show: true},// 英语
  {name: 'Deutsch', value: 'de', code: 'de', show: true},// 德语
  {name: 'Français', value: 'fr', code: 'fr', show: true},  // 法语
  {name: 'Русский', value: 'ru', code: 'ru', show: true}, // 俄语
  {name: 'Español', value: 'es', code: 'es', show: true}, // 西班牙语
  {name: 'Português', value: 'pt', code: 'pt', show: true}, // 葡萄牙语
  {name: 'Italiano', value: 'it', code: 'it', show: true},  // 意大利语
  {name: 'Melayu', value: 'ms', code: 'ms', show: true},  // 马来语
  {name: 'Afrikaans', value: 'af-ZA', code: 'af', show: true},  // 南非荷兰语
  {name: 'Ελληνικά', value: 'el', code: 'el', show: true},  // 希腊语
  {name: '繁體中文', value: 'zh-TW', code: 'zh-TW', show: true},// 繁体中文
  // {name: '简体中文', value: 'zh-CN', code: 'zh-CN', show: true},// 简体中文
  {name: 'Türkçe', value: 'tr-TR', code: 'tr', show: true}, // 土耳其语
  {name: '日本語', value: 'ja', code: 'ja', show: true}, // 日语
  {name: '한국어', value: 'ko', code: 'ko', show: true}, // 韩语
  {name: 'ภาษาไทย', value: 'th', code: 'th', show: true}, // 泰语
  {name: 'Filipino', value: 'ph', code: 'ph', show: true}, // 菲律宾语
  {name: 'العربية', value: 'ar', code: 'ar', show: true}, // 阿拉伯语
]

let splitArray = [];
const translateArray = async () => {
  for (let i = 0; i < languageArray.length; i++) {
    for (let i1 = 0; i1 < langArray.length; i1++) {
      const sheetsItem = langArray[i1];
      splitArray = [];
      for (let i2 = 0; i2 < sheetsItem.length; i2++) {
        // 对当前语言进行拆分成100个一组的数组
        if (i2 % 300 === 0 || splitArray[splitArray.length - 1].join('').length > 3000) {
          splitArray.push([])
        }
        splitArray[splitArray.length - 1].push(sheetsItem[i2]['zh-CN'] || sheetsItem[i2].key)
      }
      let translateArray = [];
      for (let i2 = 0; i2 < splitArray.length; i2++) {
        const splitArrayItem = splitArray[i2];
        let str = splitArrayItem.join('\r\n')
        console.log(sheets2[i1].name + '[' + languageArray[i].code + ']内容翻译中... ' + (i2 + 1) + '/' + splitArray.length)
        const res = await translateFunction(str, languageArray[i])
        let resArray = res.split('\r\n')
        // if (resArray.length !== 100) {
        // }
        resArray.forEach((item, index) => {
          translateArray.push(item)
        })
      }
      console.log('%c-----' + sheets2[i1].name + '[' + languageArray[i].code + ']翻译完成-----', 'color: #409EFF')
      for (let i2 = 0; i2 < sheetsItem.length; i2++) {
        if (i2 < translateArray.length) {
          langArray.forEach((item, index) => {
            item.forEach((item1, index1) => {
              if (item1['zh-CN'] === sheetsItem[i2]['zh-CN']) {
                if (languageArray[i].code === 'en') { // 英语为空时，使用翻译的内容
                  if (!item1[languageArray[i].code]) {
                    item1[languageArray[i].code] = translateArray[i2]
                  }
                } else {
                  item1[languageArray[i].code] = translateArray[i2]
                }
              }
            })
          })
        }
      }
    }
  }
  let tables = [];
  langArray.forEach((item, index) => {
    let arr = []
    arr.unshift(titleArray)
    item.forEach((item1, index1) => {
      let row = []
      for (let key in item1) {
        row.push(item1[key])
      }
      arr.push(row)
    })
    tables.push({
      name: sheets2[index].name,
      data: arr
    })
  })
  const buffer = xlsx.build(tables);
  // 写入文件
  fs.writeFile('商城国际化翻译文档3.xlsx', buffer, function (err) {
    if (err) {
      console.log("Write failed: " + err);
      return;
    }
    console.log("Write completed.");
  });

}


const translateFunction = (str, languageItem) => {
  return new Promise((resolve, reject) => {
    translate(str, {to: languageItem.code}).then(res => {
      resolve(res.text)
    }).catch(err => {
      reject(err)
    });
  })
}

translateArray()
