import Axios from "@/util/http";
//是否有资格
export const isCredit = (data) => 
Axios.fetch(`/api/credit!check.action`, data);
//申请贷款
export const Application = (data) =>
Axios.fetch(`/api/credit!apply.action`, data);
// 正在进行
export const BillCredit = (data) => 
Axios.fetch(`/api/credit!bill.action`,data)
// 申请历史
export const CreditHistory = (data) => 
Axios.fetch(`/api/credit!histroy.action`,data)
// 还款详情
export const BeforePayCredit = (data) =>
Axios.fetch(`/api/credit!beforepay.action`,data)
// 还款
export const payCredit = (data) =>
Axios.fetch(`/api/credit!pay.action`,data) 
// 贷款配置
export const creditConfig = (data) =>
Axios.fetch(`/api/credit!config.action`,data)

export const beforereapply = (data) =>
Axios.fetch(`/api/credit!beforereapply.action`,data)