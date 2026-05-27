import { ref } from 'vue'
import { getImg } from '@/utils'

const block1 = getImg('activity/turntable/block1.png')
const block2 = getImg('activity/turntable/block2.png')

export const letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
export const numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
export const emailsSuffix = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outllok.com', 'qq.com', '163.com', '126.com', 'sina.com', 'sohu.com', '139.com', '189.com', '360.com', '21cn.com', '139.com', '189.cn', 'wo.cn', 'aol.com', 'protonmail.com', 'zoho.com', 'icloud.com', 'mail.ru', 't-online.de', 'orange.fr', 'yahoo.co.uk', 'libero.it', 'yandex.ru', 'yahoo.com.sg', 'naver.com', 'saudi.net', 'rediffmail.com', 'indiatimes.com', 'yahoo.co.in', 'sify.com', 'naukri.com']


export const prizes = ref([
  {
    x: 0,
    y: 0,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  },
  {
    x: 1,
    y: 0,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  },
  {
    x: 2,
    y: 0,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  },
  {
    x: 2,
    y: 1,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  },
  {
    x: 2,
    y: 2,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  },
  {
    x: 1,
    y: 2,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  },
  {
    x: 0,
    y: 2,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  },
  {
    x: 0,
    y: 1,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  },
  {
    x: 1,
    y: 1,
    fonts: [{
      text: '',
      fontColor: '#ffffff',
      fontSize: '16px',
      top: '70%'
    }],
    imgs: [
      {
        src: block1,
        width: '100%',
        height: '100%',
        activeSrc: block2
      }
    ]
  }
])