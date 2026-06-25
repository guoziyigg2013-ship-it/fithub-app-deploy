const runtimeConfig = window.__FITHUB_CONFIG__ || {};
const API_ORIGIN = String(runtimeConfig.apiOrigin || "").replace(/\/$/, "");
const API_BASE = `${API_ORIGIN}/api`;
const TOKEN_KEY = "fithub_admin_token";

const state = {
  token: localStorage.getItem(TOKEN_KEY) || "",
  dashboard: null
};

const elements = {
  token: document.getElementById("adminToken"),
  load: document.getElementById("loadDashboard"),
  status: document.getElementById("adminStatus"),
  summary: document.getElementById("summaryGrid"),
  layout: document.getElementById("opsLayout"),
  reports: document.getElementById("reportsList"),
  queue: document.getElementById("queueList"),
  deletions: document.getElementById("deletionList"),
  actions: document.getElementById("actionsList"),
  reportCount: document.getElementById("reportCount"),
  queueCount: document.getElementById("queueCount"),
  deletionCount: document.getElementById("deletionCount")
};

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.classList.toggle("is-error", Boolean(isError));
}

async function requestAdmin(path, options = {}) {
  const token = state.token.trim();
  if (!token) {
    throw new Error("请先输入管理员 Token。");
  }
  const headers = {
    Authorization: `Bearer ${token}`,
    ...(options.headers || {})
  };
  if (options.body) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    cache: "no-store"
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || `请求失败：${response.status}`);
  }
  return payload;
}

function profileName(profile) {
  return (profile && profile.name) || "未知用户";
}

function itemTime(item) {
  return item.updatedAt || item.createdAt || item.resolvedAt || "";
}

function renderFlags(flags) {
  const list = Array.isArray(flags) ? flags : [];
  if (!list.length) return "";
  return `<div class="item-flags">${list.map((flag) => `<span class="flag">${escapeHtml(flag)}</span>`).join("")}</div>`;
}

function itemCard(item, kind, actions = true) {
  const title = item.reason || item.type || item.targetType || item.kind || "待处理项目";
  const owner = profileName(item.targetOwnerProfile);
  const reporter = profileName(item.reporterProfile);
  const meta = [
    item.targetType || item.type || kind,
    item.targetId ? `ID ${item.targetId}` : "",
    itemTime(item)
  ].filter(Boolean).join(" · ");
  return `
    <article class="ops-item" data-kind="${escapeHtml(kind)}" data-id="${escapeHtml(item.id)}">
      <div class="item-top">
        <div>
          <div class="item-title">${escapeHtml(title)}</div>
          <div class="item-meta">对象：${escapeHtml(owner)} · 提交人：${escapeHtml(reporter)}</div>
        </div>
        <span class="item-kind">${escapeHtml(item.status || "pending")}</span>
      </div>
      <div class="item-meta">${escapeHtml(meta)}</div>
      ${item.excerpt || item.detail ? `<p class="item-excerpt">${escapeHtml(item.excerpt || item.detail)}</p>` : ""}
      ${renderFlags(item.flags)}
      ${
        actions
          ? `<div class="item-actions">
              <button type="button" data-resolve-kind="${escapeHtml(kind)}" data-id="${escapeHtml(item.id)}" data-status="resolved">处理完成</button>
              <button class="secondary" type="button" data-resolve-kind="${escapeHtml(kind)}" data-id="${escapeHtml(item.id)}" data-status="dismissed">忽略</button>
            </div>`
          : ""
      }
    </article>
  `;
}

function emptyState(text) {
  return `<div class="empty-state">${escapeHtml(text)}</div>`;
}

function openItems(items, statusKey = "open") {
  return (items || []).filter((item) => (item.status || statusKey) === statusKey || item.status === "pending");
}

function renderSummary(summary) {
  const cards = [
    ["待处理举报", summary.openReports || 0],
    ["待审核内容", summary.pendingReview || 0],
    ["注销申请", summary.pendingDeletionRequests || 0],
    ["历史处理", (state.dashboard.adminActions || []).length]
  ];
  elements.summary.innerHTML = cards
    .map(([label, value]) => `<article class="summary-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></article>`)
    .join("");
  elements.summary.hidden = false;
}

function renderList(target, items, kind, emptyText) {
  if (!items.length) {
    target.innerHTML = emptyState(emptyText);
    return;
  }
  target.innerHTML = items.map((item) => itemCard(item, kind)).join("");
}

function renderActions(items) {
  if (!items.length) {
    elements.actions.innerHTML = emptyState("还没有后台处理记录。");
    return;
  }
  elements.actions.innerHTML = items
    .slice(0, 12)
    .map((item) => `
      <article class="ops-item">
        <div class="item-top">
          <div class="item-title">${escapeHtml(item.kind || "admin-action")}</div>
          <span class="item-kind">${escapeHtml(item.status || "resolved")}</span>
        </div>
        <div class="item-meta">${escapeHtml(item.targetId || "")} · ${escapeHtml(item.createdAt || "")}</div>
      </article>
    `)
    .join("");
}

function renderDashboard(payload) {
  state.dashboard = payload;
  const reports = openItems(payload.reports || [], "open");
  const queue = openItems(payload.moderationQueue || [], "pending");
  const deletions = openItems(payload.deletionRequests || [], "pending");
  renderSummary(payload.summary || {});
  elements.reportCount.textContent = reports.length;
  elements.queueCount.textContent = queue.length;
  elements.deletionCount.textContent = deletions.length;
  renderList(elements.reports, reports, "report", "暂时没有用户举报。");
  renderList(elements.queue, queue, "queue", "暂时没有待审核内容。");
  renderList(elements.deletions, deletions, "deletion", "暂时没有账号注销申请。");
  renderActions(payload.adminActions || []);
  elements.layout.hidden = false;
}

async function loadDashboard() {
  state.token = elements.token.value.trim();
  localStorage.setItem(TOKEN_KEY, state.token);
  elements.load.disabled = true;
  setStatus("正在加载审核后台...");
  try {
    const payload = await requestAdmin("/admin/moderation");
    renderDashboard(payload);
    setStatus("后台数据已同步。");
  } catch (error) {
    setStatus(error.message || "后台加载失败。", true);
  } finally {
    elements.load.disabled = false;
  }
}

async function resolveItem(kind, id, status) {
  setStatus("正在提交处理结果...");
  try {
    const payload = await requestAdmin("/admin/moderation/resolve", {
      method: "POST",
      body: JSON.stringify({
        kind,
        id,
        status,
        note: status === "dismissed" ? "运营后台忽略" : "运营后台处理完成"
      })
    });
    renderDashboard(payload);
    setStatus(status === "dismissed" ? "已忽略该项目。" : "已处理完成。");
  } catch (error) {
    setStatus(error.message || "处理失败，请重试。", true);
  }
}

elements.token.value = state.token;
elements.load.addEventListener("click", loadDashboard);
document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-resolve-kind]");
  if (!button) return;
  resolveItem(button.dataset.resolveKind, button.dataset.id, button.dataset.status);
});

if (state.token) {
  loadDashboard();
}
