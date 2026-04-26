const api = require("../../utils/api");

Page({
  data: {
    loading: true,
    bookings: [],
    targets: []
  },

  onShow() {
    this.load();
  },

  async load() {
    try {
      const payload = await api.bootstrap();
      const targets = (payload.profiles || [])
        .filter((profile) => profile.listed && (profile.role === "gym" || profile.role === "coach"))
        .slice(0, 12);
      this.setData({
        loading: false,
        bookings: payload.bookings || [],
        targets
      });
    } catch (error) {
      this.setData({ loading: false });
      api.toast(error.message);
    }
  },

  async createBooking(event) {
    try {
      await api.post("/booking/create", {
        targetProfileId: event.currentTarget.dataset.id,
        time: "本周六 20:00"
      });
      api.toast("预约已提交");
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  }
});
