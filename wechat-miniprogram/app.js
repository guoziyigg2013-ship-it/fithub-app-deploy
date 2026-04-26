const config = require("./config");

App({
  globalData: {
    apiBase: config.apiBase,
    defaultCity: config.defaultCity,
    bootstrap: null
  }
});
