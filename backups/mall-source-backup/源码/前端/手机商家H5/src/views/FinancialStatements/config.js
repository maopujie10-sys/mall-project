export const reportData = [
  {
    title: '待到账金额',
    number: 0,
    color: '#41A3FF',
    prefix: '$',
    decimals: 2,
    key: 'willIncome'
  },
  {
    title: '总销售额',
    number: 0,
    color: '#54C1FF',
    prefix: '$',
    decimals: 2,
    key: 'totalSales'
  },
  {
    title: '总利润',
    number: 0,
    color: '#3CCDC4',
    prefix: '$',
    decimals: 2,
    key: 'totalProfit'
  },
  {
    title: '总订单',
    number: 0,
    color: '#FF6F4F',
    prefix: '',
    decimals: 0,
    key: 'orderNum'
  },
  {
    title: '取消订单',
    number: 0,
    color: '#757F8F',
    prefix: '',
    decimals: 0,
    key: 'orderCancel'
  },
  {
    title: '退款订单',
    number: 0,
    color: '#DD4E4E',
    prefix: '',
    decimals: 0,
    key: 'orderReturns'
  }
]

export const reportFilter = [
  {
    name: '全部',
    value: 0
  },
  {
    name: '今日',
    value: 1
  },
  {
    name: '昨日',
    value: 2
  },
  {
    name: '本周',
    value: 3
  },
  {
    name: '本月',
    value: 4
  },
  {
    name: '本年',
    value: 5
  }
]
