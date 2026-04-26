const api = require("../../utils/api");

Page({
  data: {
    loading: true,
    recommendations: [],
    feed: []
  },

  onShow() {
    this.load();
  },

  async load() {
    try {
      const payload = await api.bootstrap();
      const follows = new Set(payload.followSet || []);
      const recommendations = (payload.profiles || [])
        .filter((profile) => profile.listed && !follows.has(profile.id))
        .slice(0, 12);
      this.setData({
        loading: false,
        recommendations,
        feed: api.followedFeed(payload)
      });
    } catch (error) {
      this.setData({ loading: false });
      api.toast(error.message);
    }
  },

  goPublish() {
    wx.navigateTo({ url: "/pages/publish/index" });
  },

  async follow(event) {
    try {
      await api.post("/follow/toggle", { targetProfileId: event.currentTarget.dataset.id });
      api.toast("已关注");
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  },

  async like(event) {
    try {
      await api.post("/post/like", { postId: event.currentTarget.dataset.id, compact: true });
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  },

  async favorite(event) {
    try {
      await api.post("/post/favorite-toggle", { postId: event.currentTarget.dataset.id, compact: true });
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  },

  async report(event) {
    try {
      await api.post("/report/create", {
        targetType: "post",
        targetId: event.currentTarget.dataset.id,
        reason: "不适内容",
        compact: true
      });
      api.toast("已收到举报");
    } catch (error) {
      api.toast(error.message);
    }
  }
});
