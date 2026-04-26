const api = require("../../utils/api");
const mediaUtil = require("../../utils/media");

Page({
  data: {
    content: "",
    media: [],
    uploading: false,
    profileId: ""
  },

  async onLoad() {
    try {
      const payload = await api.bootstrap();
      const profile = api.currentProfile(payload);
      this.setData({ profileId: profile ? profile.id : "" });
    } catch (error) {
      api.toast(error.message);
    }
  },

  onContentInput(event) {
    this.setData({ content: event.detail.value });
  },

  async chooseMedia() {
    try {
      const files = await mediaUtil.chooseMedia();
      const previews = files.map((file) => ({
        tempFilePath: file.tempFilePath,
        type: file.fileType || "image"
      }));
      this.setData({ media: previews.slice(0, 4) });
    } catch (error) {
      if (!String(error.message).includes("cancel")) api.toast(error.message);
    }
  },

  async publish() {
    const content = this.data.content.trim();
    if (!content) {
      api.toast("写点训练内容再发布");
      return;
    }
    if (!this.data.profileId) {
      api.toast("请先登录或注册");
      wx.switchTab({ url: "/pages/me/index" });
      return;
    }

    this.setData({ uploading: true });
    try {
      const uploadedMedia = [];
      for (const file of this.data.media) {
        const dataUrl = await mediaUtil.fileToDataUrl(file, file.type);
        const uploaded = await api.post("/media/upload", {
          dataUrl,
          fileName: file.type === "video" ? "wechat-video.mp4" : "wechat-image.jpg",
          assetType: file.type === "video" ? "video" : "image",
          category: "posts"
        });
        if (uploaded.media) uploadedMedia.push(uploaded.media);
      }
      await api.post("/post/create", {
        profileId: this.data.profileId,
        content,
        meta: "微信小程序 · 训练动态",
        media: uploadedMedia
      });
      api.toast("已发布");
      wx.navigateBack();
    } catch (error) {
      api.toast(error.message);
    } finally {
      this.setData({ uploading: false });
    }
  }
});
