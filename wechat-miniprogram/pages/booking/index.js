const api = require("../../utils/api");

const durationOptions = [
  { label: "45 分钟", value: 45 },
  { label: "60 分钟", value: 60 },
  { label: "90 分钟", value: 90 },
  { label: "120 分钟", value: 120 }
];

function pad(value) {
  return String(value).padStart(2, "0");
}

function dateOffset(days = 0) {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

function roleLabel(role) {
  if (role === "coach") return "健身教练";
  if (role === "gym") return "健身房";
  return "健身爱好者";
}

function formatSlot(slot = {}) {
  const duration = Number(slot.durationMinutes || 60);
  return `${slot.date || "日期待定"} ${slot.time || "时间待定"} · ${duration} 分钟`;
}

function normalizeSlot(slot = {}) {
  return {
    ...slot,
    label: formatSlot(slot),
    isBooked: (slot.status || "open") !== "open"
  };
}

function normalizeBooking(booking = {}, myProfile = {}) {
  const status = booking.status || "待确认";
  const direction = booking.direction || "outgoing";
  const isProvider = myProfile.role === "coach" || myProfile.role === "gym";
  const scheduleText = booking.scheduledDate || booking.scheduledTime
    ? formatSlot(booking)
    : booking.time || "待确认";
  return {
    ...booking,
    scheduleText,
    titleText: booking.title || `${booking.counterpartProfileName || "平台用户"} · 预约记录`,
    metaText: isProvider
      ? `${booking.counterpartProfileName || "预约人"} · ${roleLabel(booking.counterpartProfileRole)}`
      : `${booking.counterpartProfileName || booking.targetProfileName || "服务方"} · ${roleLabel(booking.counterpartProfileRole || booking.targetProfileRole)}`,
    canConfirm: isProvider && direction === "incoming" && (status === "已预约" || status === "待确认"),
    canComplete: isProvider && direction === "incoming" && status === "已确认",
    canCancel: status !== "已取消" && status !== "已完成"
  };
}

Page({
  data: {
    loading: true,
    myProfile: null,
    isProvider: false,
    bookings: [],
    targets: [],
    durationOptions,
    durationIndex: 1,
    form: {
      date: dateOffset(1),
      time: "18:30",
      note: ""
    }
  },

  onShow() {
    this.load();
  },

  async load() {
    try {
      const payload = await api.bootstrap();
      const myProfile = api.currentProfile(payload);
      const isProvider = myProfile && (myProfile.role === "coach" || myProfile.role === "gym");
      const targets = (payload.profiles || [])
        .filter((profile) => profile.listed && (profile.role === "gym" || profile.role === "coach") && profile.id !== (myProfile && myProfile.id))
        .map((profile) => ({
          ...profile,
          roleText: roleLabel(profile.role),
          openSlots: (profile.availabilitySlots || []).filter((slot) => (slot.status || "open") === "open").map(normalizeSlot)
        }))
        .filter((profile) => profile.openSlots.length || !isProvider)
        .slice(0, 12);
      const ownSlots = ((myProfile && myProfile.availabilitySlots) || []).map(normalizeSlot);
      this.setData({
        loading: false,
        myProfile,
        isProvider,
        bookings: (payload.bookings || []).map((booking) => normalizeBooking(booking, myProfile || {})),
        ownSlots,
        targets
      });
    } catch (error) {
      this.setData({ loading: false });
      api.toast(error.message);
    }
  },

  onDateChange(event) {
    this.setData({ "form.date": event.detail.value });
  },

  onTimeChange(event) {
    this.setData({ "form.time": event.detail.value });
  },

  onDurationChange(event) {
    this.setData({ durationIndex: Number(event.detail.value || 0) });
  },

  onNoteInput(event) {
    this.setData({ "form.note": event.detail.value });
  },

  async createAvailability() {
    if (!this.data.myProfile || !this.data.isProvider) {
      api.toast("请先切换到教练或健身房身份");
      return;
    }
    try {
      const duration = durationOptions[this.data.durationIndex] || durationOptions[1];
      await api.post("/availability/create", {
        profileId: this.data.myProfile.id,
        date: this.data.form.date,
        time: this.data.form.time,
        durationMinutes: duration.value,
        note: this.data.form.note
      });
      api.toast("已发布可预约时间");
      this.setData({ "form.note": "" });
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  },

  async deleteAvailability(event) {
    try {
      await api.post("/availability/delete", {
        profileId: this.data.myProfile && this.data.myProfile.id,
        slotId: event.currentTarget.dataset.slotId
      });
      api.toast("已取消这个时间");
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  },

  async createBooking(event) {
    try {
      await api.post("/booking/create", {
        targetProfileId: event.currentTarget.dataset.id,
        availabilitySlotId: event.currentTarget.dataset.slotId
      });
      api.toast("预约已提交");
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  },

  async updateBookingStatus(event) {
    try {
      await api.post("/booking/update-status", {
        bookingId: event.currentTarget.dataset.bookingId,
        status: event.currentTarget.dataset.status
      });
      api.toast("预约已更新");
      this.load();
    } catch (error) {
      api.toast(error.message);
    }
  }
});
