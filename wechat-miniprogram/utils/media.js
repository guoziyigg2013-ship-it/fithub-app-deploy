function chooseMedia() {
  return new Promise((resolve, reject) => {
    wx.chooseMedia({
      count: 4,
      mediaType: ["image", "video"],
      sourceType: ["album", "camera"],
      maxDuration: 30,
      success(result) {
        resolve(result.tempFiles || []);
      },
      fail(error) {
        reject(new Error(error.errMsg || "选择媒体失败"));
      }
    });
  });
}

module.exports = {
  chooseMedia
};
