const API_URL = "http://localhost:8000";
const state = {
  token: null,
  user: null,
  moodChart: null,
  recognition: null,
  speaking: false,
};

const selectors = {
  authSection: document.getElementById("auth"),
  dashboard: document.getElementById("dashboard"),
  registerForm: document.getElementById("register-form"),
  loginForm: document.getElementById("login-form"),
  chatForm: document.getElementById("chat-form"),
  chatWindow: document.getElementById("chat-window"),
  logout: document.getElementById("logout"),
  profileName: document.getElementById("profile-name"),
  profileEmail: document.getElementById("profile-email"),
  historyToggle: document.getElementById("history-toggle"),
  speakBtn: document.getElementById("speak-btn"),
  moodChart: document.getElementById("mood-chart"),
};

const avatar = {
  app: null,
  face: null,
  mood: "calm",
};

function initPixiAvatar() {
  if (avatar.app) return;
  avatar.app = new PIXI.Application({ view: document.getElementById("avatar"), width: 160, height: 160, backgroundAlpha: 0 });
  const container = new PIXI.Container();
  avatar.app.stage.addChild(container);

  const face = new PIXI.Graphics();
  face.beginFill(0xfff2d1).drawCircle(80, 80, 70).endFill();
  container.addChild(face);

  const leftEye = new PIXI.Graphics();
  leftEye.beginFill(0x000000).drawCircle(55, 70, 8).endFill();
  const rightEye = new PIXI.Graphics();
  rightEye.beginFill(0x000000).drawCircle(105, 70, 8).endFill();

  const mouth = new PIXI.Graphics();
  mouth.lineStyle(6, 0x8f59ff, 1);
  mouth.moveTo(55, 110).quadraticCurveTo(80, 130, 105, 110);

  container.addChild(leftEye, rightEye, mouth);

  avatar.face = { container, mouth, leftEye, rightEye };
  updateAvatarMood("calm");
}

function updateAvatarMood(mood) {
  avatar.mood = mood;
  if (!avatar.face) return;
  const { mouth, leftEye, rightEye } = avatar.face;
  mouth.clear();

  if (mood === "uplifted") {
    mouth.lineStyle(6, 0x8f59ff, 1);
    mouth.moveTo(55, 110).quadraticCurveTo(80, 140, 105, 110);
  } else if (mood === "concerned") {
    mouth.lineStyle(6, 0x8f59ff, 1);
    mouth.moveTo(55, 130).quadraticCurveTo(80, 110, 105, 130);
  } else {
    mouth.lineStyle(6, 0x8f59ff, 1);
    mouth.moveTo(55, 115).lineTo(105, 115);
  }

  const eyeScale = mood === "concerned" ? 0.8 : mood === "uplifted" ? 1.1 : 1;
  leftEye.scale.set(eyeScale);
  rightEye.scale.set(eyeScale);
}

function createMessageBubble({ sender, content, language, sentiment, created_at }) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("chat-message");
  if (sender === "ai") wrapper.classList.add("ai");

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = content;

  const meta = document.createElement("div");
  meta.classList.add("meta");
  const timestamp = new Date(created_at).toLocaleTimeString();
  meta.textContent = `${sender === "ai" ? "CompanionAI" : state.user.display_name} • ${language.toUpperCase()} • ${sentiment} • ${timestamp}`;

  wrapper.appendChild(bubble);
  wrapper.appendChild(meta);
  return wrapper;
}

function appendMessage(message) {
  const node = createMessageBubble(message);
  selectors.chatWindow.appendChild(node);
  selectors.chatWindow.scrollTop = selectors.chatWindow.scrollHeight;
}

async function api(path, options = {}) {
  const headers = options.headers ? { ...options.headers } : {};
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  if (response.status === 204) return null;
  return response.json();
}

function setToken(token) {
  state.token = token;
  if (token) {
    localStorage.setItem("companion_token", token);
  } else {
    localStorage.removeItem("companion_token");
  }
}

function setUser(user) {
  state.user = user;
  selectors.profileName.textContent = user.display_name;
  selectors.profileEmail.textContent = user.email;
  selectors.historyToggle.checked = user.history_enabled;
}

async function refreshHistory() {
  selectors.chatWindow.innerHTML = "";
  if (!state.user || !state.user.history_enabled) return;
  const history = await api("/chat/history");
  history.forEach(appendMessage);
}

async function refreshMood() {
  const entries = await api("/mood/entries");
  const sorted = entries.sort((a, b) => new Date(a.mood_date) - new Date(b.mood_date));
  const labels = sorted.map((item) => new Date(item.mood_date).toLocaleDateString());
  const data = sorted.map((item) => (item.mood === "uplifted" ? 2 : item.mood === "calm" ? 1 : 0));

  if (state.moodChart) {
    state.moodChart.data.labels = labels;
    state.moodChart.data.datasets[0].data = data;
    state.moodChart.update();
    return;
  }

  state.moodChart = new Chart(selectors.moodChart, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Mood",
          data,
          borderColor: "#5d4bff",
          backgroundColor: "rgba(93, 75, 255, 0.2)",
          fill: true,
          tension: 0.4,
        },
      ],
    },
    options: {
      scales: {
        y: {
          min: 0,
          max: 2,
          ticks: {
            callback(value) {
              return value === 2 ? "Uplifted" : value === 1 ? "Calm" : "Concerned";
            },
          },
        },
      },
    },
  });
}

async function handleRegister(event) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const payload = {
    email: formData.get("email"),
    password: formData.get("password"),
    display_name: formData.get("displayName"),
  };
  const user = await api("/auth/register", { method: "POST", body: JSON.stringify(payload) });
  alert("Account created! Please log in.");
  event.target.reset();
}

async function handleLogin(event) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const body = new URLSearchParams();
  body.append("username", formData.get("email"));
  body.append("password", formData.get("password"));
  body.append("grant_type", "password");

  const response = await fetch(`${API_URL}/auth/login`, { method: "POST", body });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Login failed" }));
    alert(error.detail || "Login failed");
    return;
  }
  const { access_token } = await response.json();
  setToken(access_token);
  await bootstrapDashboard();
}

async function bootstrapDashboard() {
  initPixiAvatar();
  const user = await api("/users/me");
  setUser(user);
  selectors.authSection.classList.add("hidden");
  selectors.dashboard.classList.remove("hidden");
  await refreshHistory();
  await refreshMood();
}

async function sendMessage(event) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const message = formData.get("message");
  if (!message.trim()) return;

  const payload = { message };
  const response = await api("/chat/respond", { method: "POST", body: JSON.stringify(payload) });
  const now = new Date().toISOString();
  appendMessage({ sender: "user", content: message, language: response.language, sentiment: response.sentiment, created_at: now });
  appendMessage({ sender: "ai", content: response.reply, language: response.language, sentiment: response.sentiment, created_at: response.timestamp });
  updateAvatarMood(response.mood);
  event.target.reset();
  await refreshMood();
}

async function toggleHistory(event) {
  const history_enabled = event.target.checked;
  const updated = await api("/users/me", { method: "PATCH", body: JSON.stringify({ history_enabled }) });
  setUser(updated);
  if (!history_enabled) {
    selectors.chatWindow.innerHTML = "";
  } else {
    await refreshHistory();
  }
}

function logout() {
  setToken(null);
  state.user = null;
  selectors.dashboard.classList.add("hidden");
  selectors.authSection.classList.remove("hidden");
  selectors.chatWindow.innerHTML = "";
}

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;
  const recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.addEventListener("result", (event) => {
    const transcript = Array.from(event.results).map((result) => result[0].transcript).join(" ");
    selectors.chatForm.message.value = transcript;
    state.speaking = false;
    selectors.speakBtn.classList.remove("active");
  });
  recognition.addEventListener("end", () => {
    state.speaking = false;
    selectors.speakBtn.classList.remove("active");
  });
  state.recognition = recognition;
}

function toggleSpeechRecognition() {
  if (!state.recognition) {
    alert("Speech recognition not supported in this browser.");
    return;
  }
  if (state.speaking) {
    state.recognition.stop();
    state.speaking = false;
    selectors.speakBtn.classList.remove("active");
  } else {
    state.recognition.start();
    state.speaking = true;
    selectors.speakBtn.classList.add("active");
  }
}

function restoreSession() {
  const token = localStorage.getItem("companion_token");
  if (token) {
    state.token = token;
    bootstrapDashboard().catch(() => logout());
  }
}

selectors.registerForm.addEventListener("submit", (event) => handleRegister(event).catch((error) => alert(error.message)));
selectors.loginForm.addEventListener("submit", (event) => handleLogin(event).catch((error) => alert(error.message)));
selectors.chatForm.addEventListener("submit", (event) => sendMessage(event).catch((error) => alert(error.message)));
selectors.logout.addEventListener("click", logout);
selectors.historyToggle.addEventListener("change", (event) => toggleHistory(event).catch((error) => alert(error.message)));
selectors.speakBtn.addEventListener("click", toggleSpeechRecognition);

initSpeechRecognition();
initPixiAvatar();
restoreSession();
