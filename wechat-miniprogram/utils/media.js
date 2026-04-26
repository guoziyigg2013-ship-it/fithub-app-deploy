function guessMimeType(path, mediaType) {
  const lower = String(path || "").toLowerCase();
  if (mediaType === "video") return "video/mp4";
  if (lower.endsWith(".png")) return "image/png";
  if (lower.endsWith(".webp")) return "image/webp";
  return "image/jpeg";
}

function fileToDataUrl(file, mediaType) {
  const fs = wx.getFileSystemManager();
  const mimeType = guessMimeType(file.tempFilePath, mediaType);
  return new Promise((resolve, reject) => {
    fs.readFile({
      filePath: file.tempFilePath,
      encoding: "base64",
      success(result) {
        resolve(`data:${mimeType};base64,${result.data}`);
      },
      fail(error) {
        reject(new Error(error.errMsg || "读取媒体文件失败"));
      }
    });
  });
}

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
  chooseMedia,
  fileToDataUrl,
  guessMimeType
};
