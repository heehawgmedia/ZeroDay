/* global marked */

// ── State ─────────────────────────────────────────────────────────────────────

let sessionId = null;
let isStreaming = false;

// ── Boot ──────────────────────────────────────────────────────────────────────

async function init() {
  await loadStatus();
  await startNewSession();
}

// ── API helpers ───────────────────────────────────────────────────────────────

async function apiFetch(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res;
}

async function loadStatus() {
  try {
    const res = await apiFetch("/api/status");
    const data = await res.json();
    renderIntegrations(data.integrations);
  } catch {
    /* non-fatal */
  }
}

async function startNewSession() {
  const res = await apiFetch("/api/sessions", { method: "POST" });
  const data = await res.json();
  sessionId = data.session_id;
  clearMessages();
}

// ── Rendering ─────────────────────────────────────────────────────────────────

function renderIntegrations(integrations) {
  const container = document.getElementById("integration-list");
  const labels = {
    github: "GitHub",
    google_analytics: "Google Analytics",
    notion: "Notion",
    linear: "Linear",
    trello: "Trello",
    files: "Local Files",
  };
  container.innerHTML = Object.entries(integrations)
    .map(([key, on]) => `
      <div class="integration-item">
        <span class="dot ${on ? "on" : "off"}"></span>
        <span>${labels[key] || key}</span>
      </div>
    `)
    .join("");
}

function clearMessages() {
  const el = document.getElementById("messages");
  el.innerHTML = "";
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
  const last = el.querySelector(".message.assistant:last-child");

  const indicator = document.createElement("div");
  indicator.className = `tool-indicator${done ? " tool-done" : ""}`;
  indicator.dataset.tool = name;

  const spinner = document.createElement("div");
  spinner.className = "tool-spinner";
  if (done) spinner.textContent = "✓";

  const label = document.createTextNode(
    done ? `Finished: ${formatToolName(name)}` : `Querying: ${formatToolName(name)}…`
  );

  indicator.append(spinner, label);

  if (last) {
    last.querySelector(".msg-bubble").before(indicator);
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

function formatToolName(name) {
  const map = {
    get_github_overview: "GitHub overview",
    get_github_issues: "GitHub issues",
    get_github_commits: "GitHub commits",
    get_analytics_summary: "Analytics",
    get_notion_tasks: "Notion tasks",
    get_linear_issues: "Linear issues",
    get_trello_cards: "Trello cards",
    read_file: "reading file",
    list_directory: "listing directory",
  };
  return map[name] || name.replace(/_/g, " ");
}

function renderMarkdown(text) {
  if (typeof marked !== "undefined") {
    return marked.parse(text, { breaks: true, gfm: true });
  }
  // Fallback: basic escaping + line breaks
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n/g, "<br>");
}

function scrollToBottom() {
  const el = document.getElementById("messages");
  el.scrollTop = el.scrollHeight;
}

// ── Chat flow ─────────────────────────────────────────────────────────────────

async function sendMessage(text) {
  if (isStreaming || !text.trim() || !sessionId) return;

  isStreaming = true;
  setSendEnabled(false);

  addMessage("user", text);

  // Prepare assistant bubble
  const assistantBubble = addMessage("assistant");
  const cursor = document.createElement("span");
  cursor.className = "cursor";
  assistantBubble.appendChild(cursor);

  let rawText = "";
  let currentToolName = null;

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
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // keep incomplete chunk

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;

        let event;
        try { event = JSON.parse(jsonStr); } catch { continue; }

        if (event.type === "tool_start") {
          currentToolName = event.name;
          addToolIndicator(event.name, false);
        } else if (event.type === "tool_done") {
          // Mark the pending indicator as done
          const indicators = document.querySelectorAll(`.tool-indicator[data-tool="${event.name}"]`);
          indicators.forEach(ind => {
            if (!ind.classList.contains("tool-done")) {
              ind.classList.add("tool-done");
              ind.querySelector(".tool-spinner").textContent = "✓";
              ind.lastChild.textContent = ` Finished: ${formatToolName(event.name)}`;
            }
          });
        } else if (event.type === "text") {
          rawText += event.content;
          // Remove cursor, re-render markdown, re-add cursor
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
          assistantBubble.innerHTML = `<span style="color:var(--error)">Error: ${event.message}</span>`;
        }
      }
    }
  } catch (err) {
    cursor.remove();
    assistantBubble.innerHTML = `<span style="color:var(--error)">Connection error: ${err.message}</span>`;
  } finally {
    cursor.remove();
    isStreaming = false;
    setSendEnabled(true);
    document.getElementById("user-input").focus();
  }
}

function setSendEnabled(enabled) {
  document.getElementById("send-btn").disabled = !enabled;
}

// ── Event listeners ───────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  init();

  const input = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");

  sendBtn.addEventListener("click", () => {
    const text = input.value.trim();
    if (text) {
      input.value = "";
      input.style.height = "22px";
      sendMessage(text);
    }
  });

  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendBtn.click();
    }
  });

  // Auto-resize textarea
  input.addEventListener("input", () => {
    input.style.height = "22px";
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
  });

  // Quick action buttons
  document.querySelectorAll(".quick-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      input.value = btn.dataset.prompt;
      sendBtn.click();
    });
  });

  // Suggestion chips
  document.querySelectorAll(".suggestion").forEach(s => {
    s.addEventListener("click", () => {
      sendMessage(s.textContent.trim());
    });
  });

  // New chat
  document.getElementById("new-chat-btn").addEventListener("click", async () => {
    if (isStreaming) return;
    await startNewSession();
  });
});
