const api = require("../../utils/api");

Page({
  data: {
    loading: true,
    tab: "gym",
    city: "厦门 · 思明区",
    gyms: [],
    coaches: []
  },

  onShow() {
    this.load();
  },

  async load() {
    try {
      const payload = await api.bootstrap();
      const position = payload.session && payload.session.userPosition;
      this.setData({
        loading: false,
        city: position && position.label || "厦门 · 思明区",
        gyms: api.listedProfiles(payload, "gym"),
        coaches: api.listedProfiles(payload, "coach")
      });
    } catch (error) {
      this.setData({ loading: false });
      api.toast(error.message);
    }
  },

  switchTab(event) {
    this.setData({ tab: event.currentTarget.dataset.tab });
  },

  async follow(event) {
    try {
      await api.post("/follow/toggle", { targetProfileId: event.currentTarget.dataset.id });
      api.toast("已更新关注");
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  },

  goProfile(event) {
    wx.navigateTo({
      url: `/pages/booking/index?target=${event.currentTarget.dataset.id}`
    });
  }
});
