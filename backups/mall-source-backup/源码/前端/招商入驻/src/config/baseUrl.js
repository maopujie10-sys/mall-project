import config from "./index";

export default process.env.NODE_ENV === "development" ? config.baseUrl.dev : config.baseUrl.pro;