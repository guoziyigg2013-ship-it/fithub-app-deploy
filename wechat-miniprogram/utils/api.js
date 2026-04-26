const config = require("../config");

function getSessionId() {
  return wx.getStorageSync("fithub_session_id") || "";
}

function setSessionId(sessionId) {
  if (sessionId) {
    wx.setStorageSync("fithub_session_id", sessionId);
  }
}

function request(path, options = {}) {
  const method = options.method || "GET";
  const data = options.data || {};
  const sessionId = getSessionId();
  const payload = method === "POST" ? { sessionId, ...data } : data;

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${config.apiBase}${path}`,
      method,
      data: payload,
      header: {
        "content-type": "application/json"
      },
      success(response) {
        const body = response.data || {};
        if (response.statusCode >= 200 && response.statusCode < 300) {
          if (body.session && body.session.id) {
            setSessionId(body.session.id);
          }
          resolve(body);
          return;
        }
        reject(new Error(body.error || "请求失败，请稍后再试"));
      },
      fail(error) {
        reject(new Error(error.errMsg || "网络连接失败"));
      }
    });
  });
}

function bootstrap() {
  const sessionId = getSessionId();
  const suffix = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : "";
  return request(`/bootstrap${suffix}`);
}

function post(path, data) {
  return request(path, { method: "POST", data });
}

function toast(message) {
  wx.showToast({
    title: message,
    icon: "none",
    duration: 1600
  });
}

function currentProfile(payload) {
  const currentId = payload && payload.session && payload.session.currentActorProfileId;
  return (payload && payload.profiles || []).find((profile) => profile.id === currentId) || null;
}

function listedProfiles(payload, role) {
  return (payload && payload.profiles || [])
    .filter((profile) => profile.listed && (!role || profile.role === role))
    .slice(0, 12);
}

function followedFeed(payload) {
  const followSet = new Set(payload && payload.followSet || []);
  return (payload && payload.profiles || [])
    .filter((profile) => followSet.has(profile.id))
    .flatMap((profile) => (profile.posts || []).map((post) => ({ profile, post })))
    .sort((a, b) => String(b.post.createdAt || "").localeCompare(String(a.post.createdAt || "")))
    .slice(0, 30);
}

module.exports = {
  bootstrap,
  post,
  request,
  toast,
  currentProfile,
  listedProfiles,
  followedFeed,
  getSessionId,
  setSessionId
};
