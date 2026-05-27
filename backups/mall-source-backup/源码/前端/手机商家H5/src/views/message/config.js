export const msgTypeInfo = {
  inbox_finish_order: {
    title: '订单完成通知',
    txt: '已完成交易，佣金已成功发放至您的账户余额。订单号：',
    key: 'orderNo'
  },
  inbox_freeze_seller_money: {
    title: '余额冻结通知',
    txt: '由于您违反了平台规则，您的部分钱包余额已被冻结。冻结金额：',
    key: 'amount'
  },
  inbox_new_order_submitted: {
    title: '新订单通知',
    txt: '您的店铺有新订单，请及时处理订单。'
  },
  inbox_order_shipped_overtime: {
    title: '订单超时通知',
    txt: '您有订单逾期未发货，已违反平台商户规则，请尽快处理！'
  },
  inbox_reply_buyer_im: {
    title: '新访客咨询',
    txt: '您有一个新的买家咨询，已超过5分钟未回复。'
  },
  inbox_seller_credit_updated: {
    title: '信用分变更通知',
    txt: '您好，您的卖家信用评分更新为：',
    txt1: '，如有疑问，请联系客服!',
    key: 'creditScore'
  },
  inbox_unfreeze_seller_money: {
    title: '余额解冻通知',
    txt: '您的余额已解冻并存入您的钱包。解冻金额：',
    key: 'amount'
  },
  inbox_recharge_success: {
    title: '充值成功',
    key: 'inbox_recharge_success'
  },
  inbox_withdraw_success: {
    title: '提现成功',
    key: 'inbox_withdraw_success'
  },
  inbox_store_audit_fail: {
    title: '店铺认证失败',
    key: 'inbox_store_audit_fail'
  },
  inbox_store_audit_success: {
    title: '店铺认证通过',
    key: 'inbox_store_audit_success'
  },
  inbox_order_purchased_overtime: {
    title: '订单采购超时通知',
    txt: '您有订单逾期未采购，已违反平台商户规则，请尽快处理！'
  },
  inbox_store_compliant_success: {
    title: '店铺投诉通知',
    txt: '店铺投诉通知内容'
  },
  inbox_bonus_success: {
    title: '赠送彩金通知',
    txt: '您有一笔彩金到账，到账金额：',
    key: 'amount'
  },
  inbox_withdrawal_audit_fail: {
    title: '提款失败通知',
    txt: '提款失败通知内容'
  },
  inbox_recharge_audit_fail: {
    title: '存款失败通知',
    txt: '存款失败通知内容'
  }
}
