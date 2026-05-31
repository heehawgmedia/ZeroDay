/* global marked */

// ── State ─────────────────────────────────────────────────────────────────────

let sessionId = null;
let isStreaming = false;
let dashboardRefreshTimer = null;

// ── Boot ──────────────────────────────────────────────────────────────────────

async function init() {
  await Promise.all([loadStatus(), startNewSession()]);
  await loadDashboard();
  scheduleDashboardRefresh();
}

// ── API ───────────────────────────────────────────────────────────────────────

async function apiFetch(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(body || `${res.status} ${res.statusText}`);
  }
  return res;
}

async function loadStatus() {
  try {
    const data = await (await apiFetch("/api/status")).json();
    renderIntegrations(data.integrations);
  } catch { /* non-fatal */ }
}

async function startNewSession() {
  const data = await (await apiFetch("/api/sessions", { method: "POST" })).json();
  sessionId = data.session_id;
  clearMessages();
}

// ── Integrations sidebar ──────────────────────────────────────────────────────

function renderIntegrations(integrations) {
  const labels = {
    github: "GitHub", google_analytics: "Analytics",
    search_console: "Search Console", notion: "Notion",
    linear: "Linear", trello: "Trello", sentry: "Sentry", files: "Local Files",
  };
  document.getElementById("integration-list").innerHTML = Object.entries(integrations)
    .map(([k, on]) => `
      <div class="integration-item">
        <span class="dot ${on ? "on" : "off"}"></span>
        <span>${labels[k] || k}</span>
      </div>`)
    .join("");
}

// ── Tab switching ─────────────────────────────────────────────────────────────

function showTab(name) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  document.getElementById("tab-dashboard").style.display = name === "dashboard" ? "flex" : "none";
  document.getElementById("tab-chat").style.display     = name === "chat"      ? "flex" : "none";
  if (name === "chat") document.getElementById("user-input").focus();
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

async function loadDashboard() {
  try {
    const data = await (await apiFetch("/api/dashboard")).json();
    renderDashboard(data.sites, data.poll_interval_seconds);
  } catch (err) {
    console.error("Dashboard load failed:", err);
  }
}

function scheduleDashboardRefresh() {
  clearInterval(dashboardRefreshTimer);
  dashboardRefreshTimer = setInterval(loadDashboard, 60_000);
}

function renderDashboard(sites, pollInterval) {
  const grid = document.getElementById("site-grid");
  const noMsg = document.getElementById("no-sites-msg");

  if (!sites || sites.length === 0) {
    grid.innerHTML = "";
    grid.appendChild(noMsg);
    noMsg.style.display = "";
    return;
  }

  noMsg.style.display = "none";

  // Keep existing cards and update them; add new ones; remove stale ones
  const existingUrls = new Set([...grid.querySelectorAll(".site-card")].map(c => c.dataset.url));
  const newUrls = new Set(sites.map(s => s.url));

  // Remove cards for deleted sites
  grid.querySelectorAll(".site-card").forEach(card => {
    if (!newUrls.has(card.dataset.url)) card.remove();
  });

  for (const site of sites) {
    const existing = grid.querySelector(`.site-card[data-url="${CSS.escape(site.url)}"]`);
    const card = buildSiteCard(site, pollInterval);
    if (existing) {
      existing.replaceWith(card);
    } else {
      grid.appendChild(card);
    }
  }
}

function buildSiteCard(site, pollInterval) {
  const health   = site.health   || {};
  const pagespeed = site.pagespeed || {};
  const sentry   = site.sentry   || {};

  const status = health.status || "unknown";
  const statusClass = status === "up" ? "up" : status === "down" ? "down" : status === "degraded" ? "degraded" : "unknown";
  const cardClass = status === "up" ? "card-up" : status === "down" ? "card-down" : status === "degraded" ? "card-warn" : "card-unknown";

  // Response time color
  const ms = health.response_ms;
  const msClass = ms == null ? "dim" : ms < 500 ? "good" : ms < 1500 ? "warn" : "bad";
  const msText = ms != null ? `${ms}ms` : "—";

  // SSL
  const sslDays = health.ssl_days;
  const sslClass = sslDays == null ? "dim" : sslDays > 30 ? "good" : sslDays > 7 ? "warn" : "bad";
  const sslText = sslDays != null ? `${sslDays}d` : "—";

  // PageSpeed
  const dScore = pagespeed.desktop?.score;
  const mScore = pagespeed.mobile?.score;
  const scoreClass = s => s == null ? "dim" : s >= 90 ? "good" : s >= 50 ? "ok" : "bad";
  const scoreText = s => s != null ? s : "—";

  // Sentry
  const errCount = sentry.unresolved_count;
  const err24h   = sentry.errors_last_24h;
  const sentryText = errCount != null
    ? `${errCount} unresolved · ${err24h ?? 0} (24h)`
    : "—";
  const sentryClass = errCount == null ? "" : errCount === 0 ? "clean" : "has-errors";

  // Last checked
  const checkedAt = health.checked_at
    ? timeAgo(new Date(health.checked_at))
    : "Not checked yet";

  const card = document.createElement("div");
  card.className = `site-card ${cardClass}`;
  card.dataset.url = site.url;

  card.innerHTML = `
    <div class="card-header">
      <div class="card-title">
        <span class="status-dot ${statusClass}"></span>
        <div>
          <div class="site-name">${escHtml(site.name)}</div>
          <div class="site-url"><a href="${escHtml(site.url)}" target="_blank" rel="noopener">${escHtml(site.url)}</a></div>
        </div>
      </div>
      <div class="card-actions">
        <button class="card-btn ask-btn">Ask Jarvis</button>
        <button class="card-btn remove-btn">✕</button>
      </div>
    </div>

    <div class="card-metrics">
      <div class="metric-cell">
        <div class="metric-label">Response</div>
        <div class="metric-value ${msClass}">${msText}</div>
      </div>
      <div class="metric-cell">
        <div class="metric-label">SSL Expires</div>
        <div class="metric-value ${sslClass}">${sslText}</div>
      </div>
    </div>

    ${dScore != null || mScore != null ? `
    <div class="card-perf">
      <div class="perf-item">
        <div class="perf-label">Desktop</div>
        <div class="perf-score ${scoreClass(dScore)}">${scoreText(dScore)}</div>
      </div>
      <div class="perf-item">
        <div class="perf-label">Mobile</div>
        <div class="perf-score ${scoreClass(mScore)}">${scoreText(mScore)}</div>
      </div>
    </div>` : ""}

    ${errCount != null || sentry.checked_at ? `
    <div class="card-sentry">
      <span class="metric-label">Sentry</span>
      <span class="sentry-errors ${sentryClass}">${sentryText}</span>
    </div>` : ""}

    <div class="card-footer">Last checked: ${checkedAt}</div>
  `;

  card.querySelector(".ask-btn").addEventListener("click", () => {
    showTab("chat");
    const input = document.getElementById("user-input");
    input.value = `Analyze ${site.url} — check uptime, performance, errors, and recent activity.`;
    input.dispatchEvent(new Event("input"));
    input.focus();
  });

  card.querySelector(".remove-btn").addEventListener("click", async () => {
    if (!confirm(`Stop monitoring ${site.url}?`)) return;
    try {
      await apiFetch("/api/sites", {
        method: "DELETE",
        body: JSON.stringify({ url: site.url }),
      });
      loadDashboard();
    } catch (err) {
      alert(`Failed to remove site: ${err.message}`);
    }
  });

  return card;
}

async function addSite() {
  const urlInput  = document.getElementById("site-url-input");
  const nameInput = document.getElementById("site-name-input");
  const url  = urlInput.value.trim();
  const name = nameInput.value.trim();
  if (!url) { urlInput.focus(); return; }

  const btn = document.getElementById("add-site-btn");
  btn.disabled = true;
  btn.textContent = "Adding…";
  try {
    await apiFetch("/api/sites", {
      method: "POST",
      body: JSON.stringify({ url, name: name || undefined }),
    });
    urlInput.value = "";
    nameInput.value = "";
    await loadDashboard();
  } catch (err) {
    alert(`Could not add site: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "+ Add Site";
  }
}

// ── Chat ──────────────────────────────────────────────────────────────────────

function clearMessages() {
  document.getElementById("messages").innerHTML = "";
  document.getElementById("welcome").style.display = "flex";
}

function hideWelcome() {
  document.getElementById("welcome").style.display = "none";
}

function addMessage(role, content = "") {
  hideWelcome();
  const el = document.getElementById("messages");
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;
  const label = document.createElement("div");
  label.className = "msg-label";
  label.textContent = role === "user" ? "You" : "JARVIS";
  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = content ? renderMarkdown(content) : "";
  wrap.append(label, bubble);
  el.append(wrap);
  scrollToBottom();
  return bubble;
}

function addToolIndicator(name, done = false) {
  const el = document.getElementById("messages");
  let targetBubbleParent = el.querySelector(".message.assistant:last-child");

  const indicator = document.createElement("div");
  indicator.className = `tool-indicator${done ? " tool-done" : ""}`;
  indicator.dataset.tool = name;
  const spinner = document.createElement("div");
  spinner.className = "tool-spinner";
  if (done) spinner.textContent = "✓";
  indicator.append(spinner, document.createTextNode(
    done ? ` Done: ${fmtTool(name)}` : ` Querying: ${fmtTool(name)}…`
  ));

  if (targetBubbleParent) {
    targetBubbleParent.querySelector(".msg-bubble").before(indicator);
  } else {
    const wrap = document.createElement("div");
    wrap.className = "message assistant";
    const lbl = document.createElement("div");
    lbl.className = "msg-label";
    lbl.textContent = "JARVIS";
    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    wrap.append(lbl, indicator, bubble);
    el.append(wrap);
  }
  scrollToBottom();
}

function fmtTool(name) {
  return {
    get_github_overview: "GitHub overview", get_github_issues: "GitHub issues",
    get_github_commits: "GitHub commits", get_analytics_summary: "Analytics",
    get_notion_tasks: "Notion", get_linear_issues: "Linear", get_trello_cards: "Trello",
    check_site_health: "site health check", get_pagespeed: "PageSpeed",
    get_search_console_data: "Search Console", get_sentry_issues: "Sentry",
    manage_sites: "site registry", get_monitoring_dashboard: "dashboard snapshot",
    read_file: "reading file", list_directory: "listing directory",
  }[name] || name.replace(/_/g, " ");
}

function renderMarkdown(text) {
  return typeof marked !== "undefined"
    ? marked.parse(text, { breaks: true, gfm: true })
    : text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>");
}

function scrollToBottom() {
  const el = document.getElementById("messages");
  el.scrollTop = el.scrollHeight;
}

async function sendMessage(text) {
  if (isStreaming || !text.trim() || !sessionId) return;
  isStreaming = true;
  setSendEnabled(false);

  addMessage("user", text);
  const assistantBubble = addMessage("assistant");
  const cursor = document.createElement("span");
  cursor.className = "cursor";
  assistantBubble.appendChild(cursor);

  let rawText = "";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop();

      for (const part of parts) {
        if (!part.startsWith("data: ")) continue;
        let event;
        try { event = JSON.parse(part.slice(6)); } catch { continue; }

        if (event.type === "tool_start") {
          addToolIndicator(event.name, false);
        } else if (event.type === "tool_done") {
          document.querySelectorAll(`.tool-indicator[data-tool="${event.name}"]:not(.tool-done)`)
            .forEach(ind => {
              ind.classList.add("tool-done");
              ind.querySelector(".tool-spinner").textContent = "✓";
              ind.lastChild.textContent = ` Done: ${fmtTool(event.name)}`;
            });
          // Refresh dashboard if a site-management tool ran
          if (["manage_sites", "check_site_health"].includes(event.name)) {
            loadDashboard();
          }
        } else if (event.type === "text") {
          rawText += event.content;
          cursor.remove();
          assistantBubble.innerHTML = renderMarkdown(rawText);
          assistantBubble.appendChild(cursor);
          scrollToBottom();
        } else if (event.type === "done") {
          cursor.remove();
          assistantBubble.innerHTML = renderMarkdown(rawText);
          scrollToBottom();
        } else if (event.type === "error") {
          cursor.remove();
          assistantBubble.innerHTML = `<span style="color:var(--error)">Error: ${escHtml(event.message)}</span>`;
        }
      }
    }
  } catch (err) {
    cursor.remove();
    assistantBubble.innerHTML = `<span style="color:var(--error)">Connection error: ${escHtml(err.message)}</span>`;
  } finally {
    cursor.remove();
    isStreaming = false;
    setSendEnabled(true);
    document.getElementById("user-input").focus();
  }
}

function setSendEnabled(ok) { document.getElementById("send-btn").disabled = !ok; }

// ── Utilities ─────────────────────────────────────────────────────────────────

function escHtml(str) {
  return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function timeAgo(date) {
  const secs = Math.floor((Date.now() - date) / 1000);
  if (secs < 60)  return `${secs}s ago`;
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`;
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`;
  return `${Math.floor(secs / 86400)}d ago`;
}

// ── Event listeners ───────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  init();

  // Tabs
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => showTab(btn.dataset.tab));
  });

  // Chat input
  const input = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");

  sendBtn.addEventListener("click", () => {
    const text = input.value.trim();
    if (text) { input.value = ""; input.style.height = "22px"; sendMessage(text); }
  });

  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendBtn.click(); }
  });

  input.addEventListener("input", () => {
    input.style.height = "22px";
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
  });

  // Sidebar quick buttons route to chat tab
  document.querySelectorAll(".quick-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      showTab("chat");
      input.value = btn.dataset.prompt;
      sendBtn.click();
    });
  });

  document.querySelectorAll(".suggestion").forEach(s => {
    s.addEventListener("click", () => { showTab("chat"); sendMessage(s.textContent.trim()); });
  });

  document.getElementById("new-chat-btn").addEventListener("click", async () => {
    if (isStreaming) return;
    await startNewSession();
    showTab("chat");
  });

  // Add site
  document.getElementById("add-site-btn").addEventListener("click", addSite);
  document.getElementById("site-url-input").addEventListener("keydown", e => {
    if (e.key === "Enter") addSite();
  });
});
