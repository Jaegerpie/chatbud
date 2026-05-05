const API_BASE = "http://localhost:8000";

function $(id) {
  return document.getElementById(id);
}

function getTheme() {
  return localStorage.getItem("theme") || "dark";
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

function scrollToBottom() {
  const el = $("chatScroll");
  el.scrollTop = el.scrollHeight;
}

function addMessage(role, text, { typing = false } = {}) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role === "user" ? "msg--user" : "msg--bot"}`;

  const bubble = document.createElement("div");
  bubble.className = `bubble ${typing ? "bubble--typing" : ""}`.trim();
  bubble.textContent = text;

  wrap.appendChild(bubble);
  $("chatScroll").appendChild(wrap);
  scrollToBottom();

  return { wrap, bubble };
}

async function sendMessage(message) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  let data;
  try {
    data = await res.json();
  } catch (_) {
    throw new Error(`Backend returned non-JSON (HTTP ${res.status})`);
  }

  if (!res.ok) {
    const detail = data?.detail ? String(data.detail) : "Unknown error";
    throw new Error(detail);
  }

  if (!data || typeof data.reply !== "string") {
    throw new Error("Invalid backend response shape (expected { reply: string }).");
  }

  return data.reply;
}

function resetChat() {
  const scroll = $("chatScroll");
  scroll.innerHTML = "";
  addMessage("bot", "New chat started. What would you like to ask?");
}

function main() {
  // Theme
  setTheme(getTheme());
  $("themeToggle").addEventListener("click", () => {
    setTheme(getTheme() === "dark" ? "light" : "dark");
  });

  // New chat
  $("newChatBtn").addEventListener("click", resetChat);

  // Send
  const form = $("chatForm");
  const input = $("chatInput");
  const sendBtn = $("sendBtn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = (input.value || "").trim();
    if (!message) return;

    input.value = "";
    input.focus();

    addMessage("user", message);
    sendBtn.disabled = true;
    const typing = addMessage("bot", "Typing…", { typing: true });

    try {
      const reply = await sendMessage(message);
      typing.bubble.classList.remove("bubble--typing");
      typing.bubble.textContent = reply;
    } catch (err) {
      typing.bubble.classList.remove("bubble--typing");
      typing.bubble.textContent = `Error: ${err?.message || String(err)}`;
    } finally {
      sendBtn.disabled = false;
      scrollToBottom();
    }
  });

  // Start focused
  input.focus();
}

main();

