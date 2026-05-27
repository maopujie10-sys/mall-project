import { Message } from "element-ui";
import i18n from "@/lang/i18n";
import { ES_TOKEN } from "./constant";
// import router from "@/router.js";
export const EsMessage = (message, type = "error") => {
  Message({
    message,
    type,
  });
};

export const showI18nMessage = (message, type = 'success') => {
  EsMessage(i18n.t(message), type)
}


export const notLoginMessage = () => {
  EsMessage(i18n.t('message.home.notLogin'))
}

export const notLogin = () => {
  if (!localStorage.getItem(ES_TOKEN)) {
    notLoginMessage()
    return true;
  }
  return false
};
