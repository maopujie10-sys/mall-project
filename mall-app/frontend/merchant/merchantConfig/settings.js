module.exports = {
  projectTitle: 'Argos',
  //
  baseUrl: 'http://localhost/wap/',
  // baseUrl: 'https://www.argosshops.com/wap/',
  // baseUrl: 'https://www.argosshops.com/wap/',
  /**
   * @type {boolean} true | false
   * @description Whether show the settings right-panel
   */
  showSettings: true,
  hideContact: false,
  countryCode: "44",//默认国家代码

  /**
   * @type {boolean} true | false
   * @description Whether need tagsView
   */
  tagsView: true,

  /**
   * @type {boolean} true | false
   * @description Whether fix the header
   */
  fixedHeader: false,

  /**
   * @type {boolean} true | false
   * @description Whether show the logo in sidebar
   */
  sidebarLogo: false,

  /**
   * @type {string | array} 'production' | ['production', 'development']
   * @description Need show err logs component.
   * The default is only used in the production env
   * If you want to also use it in dev, you can pass ['production', 'development']
   */
  errorLog: 'production'
}
