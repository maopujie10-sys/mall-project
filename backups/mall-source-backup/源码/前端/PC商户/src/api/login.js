import Axios from "../util/http";
//登录
function loginApi(data) {
  return Axios.post("/api/user!newlogin.action", data);
}
//获取邮箱或手机号的验证码
// function getVeriCodeApi(data) {
//   return Axios.fetch("/api/idcode!execute.action", data);
// }
//手机号或邮箱注册
function resgisterApi(data) {
  return Axios.fetch("/api/localuser!registerNoVerifcode.action", data);
}
//根据用户名和类型获取它的验证方式，接口会返回邮箱或手机号。之前用于重置密码界面，目前此接口弃用。
function forgotVericodeApi(data) {
  return Axios.fetch("api/user!getUserNameVerifTarget.action", data);
}
//通过邮箱或手机号，或谷歌重置密码
function fixResgisterApi(data) {
  return Axios.fetch("api/user!resetpsw.action", data);
}
//退出登录
function loginOutApi() {
  return Axios.fetch("api/user!logout.action");
}
//用账户名注册时，获取接口返回的base64图片
function imageVerificaApi() {
  return Axios.fetch("api/localuser!getImageCode.action");
}
//账号名注册
function accountRegisterApi(data) {
  return Axios.fetch("api/localuser!register_username.action", data);
}
///通过谷歌验证器重置密码
function resetpswByGoogleApi(data) {
  return Axios.fetch("/api/user!resetpswByGoogle.action", data);
}
function getVeriCodeApi(data) {
  return Axios.fetch("/api/jscode!execute.action", data);
}
// Just 注册接口
function JustRegisterApi(data) {
  return Axios.fetch("/api/localuser!registerWithVerifcode.action", data);
}
export {
  loginApi,
  getVeriCodeApi,
  resgisterApi,
  forgotVericodeApi,
  fixResgisterApi,
  loginOutApi,
  imageVerificaApi,
  accountRegisterApi,
  resetpswByGoogleApi,
  JustRegisterApi
};
