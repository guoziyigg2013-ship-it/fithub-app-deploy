const api = require("../../utils/api");

Page({
  data: {
    loading: true,
    profile: null,
    phone: "",
    code: "",
    debugCode: "",
    role: "enthusiast"
  },

  onShow() {
    this.load();
  },

  async load() {
    try {
      const payload = await api.bootstrap();
      const profile = api.currentProfile(payload);
      if (profile && !Array.isArray(profile.posts)) {
        profile.posts = [];
      }
      this.setData({
        loading: false,
        profile
      });
    } catch (error) {
      this.setData({ loading: false });
      api.toast(error.message);
    }
  },

  onInput(event) {
    this.setData({ [event.currentTarget.dataset.field]: event.detail.value });
  },

  async wechatLogin() {
    try {
      const login = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        });
      });
      await api.post("/auth/wechat-mini-login", {
        code: login.code,
        role: this.data.role
      });
      api.toast("微信登录成功");
      this.load();
    } catch (error) {
      api.toast(error.message || "微信登录失败");
    }
  },

  async sendCode() {
    if (!this.data.phone) {
      api.toast("请输入手机号");
      return;
    }
    try {
      const payload = await api.post("/auth/send-code", {
        phone: this.data.phone,
        purpose: "login"
      });
      this.setData({ debugCode: payload.debugCode || "" });
      api.toast(payload.debugCode ? `测试验证码 ${payload.debugCode}` : "验证码已发送");
    } catch (error) {
      api.toast(error.message);
    }
  },

  async phoneLogin() {
    try {
      await api.post("/auth/login", {
        phone: this.data.phone,
        role: this.data.role,
        verificationCode: this.data.code
      });
      api.toast("登录成功");
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  },

  async quickRegister() {
    try {
      await api.post("/register", {
        role: "enthusiast",
        verificationCode: this.data.code,
        profile: {
          name: "微信训练者",
          phone: this.data.phone,
          gender: "男",
          heightCm: 175,
          weightKg: 70,
          level: "新手入门",
          goal: "保持规律训练"
        }
      });
      api.toast("注册成功");
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  }
});
