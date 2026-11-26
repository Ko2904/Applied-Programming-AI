function updateClock() {
  const now = new Date();
  document.getElementById("clock").textContent =
    now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
updateClock();
setInterval(updateClock, 1000);

async function showDailyQuote() {
  try {
    const response = await fetch("quotes.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const quotes = await response.json();

    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 0);
    const dayOfYear = Math.floor((now - start) / 86400000);
    const quote = quotes[dayOfYear % quotes.length];
    document.getElementById("quote-text").textContent = quote.text;
    document.getElementById("quote-author").textContent = quote.author;
  } catch (error) {
    console.error("Could not load quote:", error);
  }
}
showDailyQuote();

const PRESETS = [
  "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
  "linear-gradient(135deg, #42275a, #734b6d)",
  "linear-gradient(135deg, #134e5e, #71b280)",
  "linear-gradient(135deg, #232526, #414345)",
  "linear-gradient(135deg, #614385, #516395)",
  "linear-gradient(135deg, #b24592, #f15f79)"
];

let reminders = [];
let todos = [];
let personalGoal = { title: "", progress: 0 };

function setWidgetStatus(message) {
  document.getElementById("widget-status").textContent = message;
}

async function applyBackground() {
  try {
    const { background } = await chrome.storage.local.get("background");
    document.body.style.backgroundImage = background || "";
  } catch (error) {
    console.error("Could not load background:", error);
    setWidgetStatus("Could not load your saved background.");
  }
}

async function saveBackground(cssValue) {
  try {
    await chrome.storage.local.set({ background: cssValue });
    document.body.style.backgroundImage = cssValue || "";
  } catch (error) {
    console.error("Could not save background:", error);
    setWidgetStatus("Could not save your background.");
  }
}

function resizeImage(file, maxSize = 1920) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = () => {
      const img = new Image();
      img.onerror = reject;
      img.onload = () => {
        const scale = Math.min(1, maxSize / Math.max(img.width, img.height));
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
        canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", 0.85));
      };
      img.src = reader.result;
    };
    reader.readAsDataURL(file);
  });
}

function createEmptyState(message) {
  const item = document.createElement("li");
  item.className = "empty-state";
  item.textContent = message;
  return item;
}

function isValidReminder(item) {
  return item
    && typeof item.id === "string"
    && typeof item.text === "string"
    && typeof item.dueAt === "string"
    && Number.isFinite(Date.parse(item.dueAt))
    && typeof item.completed === "boolean";
}

function isValidTodo(item) {
  return item
    && typeof item.id === "string"
    && typeof item.text === "string"
    && typeof item.completed === "boolean";
}

function updateCount(elementId, count, label) {
  document.getElementById(elementId).textContent = `${count} ${label}`;
}

function renderReminders() {
  const list = document.getElementById("reminder-list");
  list.replaceChildren();
  const openCount = reminders.filter((reminder) => !reminder.completed).length;
  updateCount("reminder-count", openCount, "open");

  if (reminders.length === 0) {
    list.appendChild(createEmptyState("No reminders yet."));
    return;
  }

  const sorted = [...reminders].sort((first, second) => {
    if (first.completed !== second.completed) return Number(first.completed) - Number(second.completed);
    return Date.parse(first.dueAt) - Date.parse(second.dueAt);
  });

  sorted.forEach((reminder) => {
    const row = document.createElement("li");
    const due = new Date(reminder.dueAt);
    const isDue = !reminder.completed && due.getTime() <= Date.now();
    row.className = `item-row${reminder.completed ? " is-complete" : ""}${isDue ? " is-due" : ""}`;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "item-check";
    checkbox.checked = reminder.completed;
    checkbox.setAttribute("aria-label", `Mark ${reminder.text} complete`);
    checkbox.addEventListener("change", () => {
      updateReminders(reminders.map((item) =>
        item.id === reminder.id ? { ...item, completed: checkbox.checked } : item));
    });

    const details = document.createElement("div");
    details.className = "item-main";
    const title = document.createElement("span");
    title.className = "item-title";
    title.textContent = reminder.text;
    const meta = document.createElement("time");
    meta.className = "item-meta";
    meta.dateTime = reminder.dueAt;
    meta.textContent = `${due.toLocaleString()} · ${reminder.completed ? "Done" : isDue ? "Due now" : "Upcoming"}`;
    details.append(title, meta);

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "delete-button";
    removeButton.textContent = "Delete";
    removeButton.setAttribute("aria-label", `Delete reminder: ${reminder.text}`);
    removeButton.addEventListener("click", () => {
      updateReminders(reminders.filter((item) => item.id !== reminder.id));
    });

    row.append(checkbox, details, removeButton);
    list.appendChild(row);
  });
}

async function updateReminders(nextReminders) {
  try {
    await chrome.storage.local.set({ reminders: nextReminders });
    reminders = nextReminders;
    renderReminders();
    setWidgetStatus("");
  } catch (error) {
    console.error("Could not save reminders:", error);
    setWidgetStatus("Could not save your reminders. Please try again.");
  }
}

function renderTodos() {
  const list = document.getElementById("todo-list");
  list.replaceChildren();
  const openCount = todos.filter((todo) => !todo.completed).length;
  updateCount("todo-count", openCount, "left");

  if (todos.length === 0) {
    list.appendChild(createEmptyState("No tasks yet."));
    return;
  }

  todos.forEach((todo) => {
    const row = document.createElement("li");
    row.className = `item-row${todo.completed ? " is-complete" : ""}`;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "item-check";
    checkbox.checked = todo.completed;
    checkbox.setAttribute("aria-label", `Mark ${todo.text} complete`);
    checkbox.addEventListener("change", () => {
      updateTodos(todos.map((item) =>
        item.id === todo.id ? { ...item, completed: checkbox.checked } : item));
    });

    const title = document.createElement("span");
    title.className = "item-title item-main";
    title.textContent = todo.text;

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "delete-button";
    removeButton.textContent = "Delete";
    removeButton.setAttribute("aria-label", `Delete task: ${todo.text}`);
    removeButton.addEventListener("click", () => {
      updateTodos(todos.filter((item) => item.id !== todo.id));
    });

    row.append(checkbox, title, removeButton);
    list.appendChild(row);
  });
}

async function updateTodos(nextTodos) {
  try {
    await chrome.storage.local.set({ todos: nextTodos });
    todos = nextTodos;
    renderTodos();
    setWidgetStatus("");
  } catch (error) {
    console.error("Could not save tasks:", error);
    setWidgetStatus("Could not save your tasks. Please try again.");
  }
}

function renderGoal() {
  document.getElementById("goal-title").value = personalGoal.title;
  document.getElementById("goal-progress").value = String(personalGoal.progress);
  document.getElementById("goal-progress-label").textContent = `${personalGoal.progress}%`;
  document.getElementById("goal-progress-bar").value = personalGoal.progress;
}

async function saveGoal(nextGoal) {
  try {
    await chrome.storage.local.set({ personalGoal: nextGoal });
    personalGoal = nextGoal;
    renderGoal();
    setWidgetStatus("");
    return true;
  } catch (error) {
    console.error("Could not save personal goal:", error);
    setWidgetStatus("Could not save your goal. Please try again.");
    return false;
  }
}

function setupWidgets() {
  document.getElementById("reminder-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = document.getElementById("reminder-text").value.trim();
    const dueAt = new Date(document.getElementById("reminder-when").value);
    if (!text || Number.isNaN(dueAt.getTime())) {
      setWidgetStatus("Enter a reminder and a valid date and time.");
      return;
    }

    const nextReminders = [
      ...reminders,
      {
        id: crypto.randomUUID(),
        text,
        dueAt: dueAt.toISOString(),
        completed: false,
      },
    ];
    await updateReminders(nextReminders);
    if (reminders === nextReminders) {
      document.getElementById("reminder-form").reset();
      setWidgetStatus("Reminder saved.");
    }
  });

  document.getElementById("todo-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = document.getElementById("todo-text");
    const text = input.value.trim();
    if (!text) {
      setWidgetStatus("Enter a task before adding it.");
      return;
    }

    const nextTodos = [...todos, { id: crypto.randomUUID(), text, completed: false }];
    await updateTodos(nextTodos);
    if (todos === nextTodos) {
      document.getElementById("todo-form").reset();
      setWidgetStatus("Task added.");
    }
  });

  const progressInput = document.getElementById("goal-progress");
  progressInput.addEventListener("input", () => {
    const progress = Number(progressInput.value);
    document.getElementById("goal-progress-label").textContent = `${progress}%`;
    document.getElementById("goal-progress-bar").value = progress;
  });

  document.getElementById("goal-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = document.getElementById("goal-title").value.trim();
    if (!title) {
      setWidgetStatus("Enter a goal before saving it.");
      return;
    }
    const progress = Math.max(0, Math.min(100, Number(progressInput.value) || 0));
    if (await saveGoal({ title, progress })) setWidgetStatus("Goal saved.");
  });

  document.getElementById("goal-reset").addEventListener("click", async () => {
    if (await saveGoal({ title: "", progress: 0 })) setWidgetStatus("Goal cleared.");
  });
}

async function loadWidgets() {
  try {
    await chrome.storage.local.remove("newsCache");
  } catch (error) {
    console.error("Could not clear the previous news cache:", error);
    setWidgetStatus("Could not clear data from the previous news feature.");
  }

  try {
    const stored = await chrome.storage.local.get(["reminders", "todos", "personalGoal"]);
    reminders = Array.isArray(stored.reminders) ? stored.reminders.filter(isValidReminder) : [];
    todos = Array.isArray(stored.todos) ? stored.todos.filter(isValidTodo) : [];
    const goal = stored.personalGoal;
    if (goal && typeof goal.title === "string" && Number.isFinite(Number(goal.progress))) {
      personalGoal = {
        title: goal.title,
        progress: Math.max(0, Math.min(100, Number(goal.progress))),
      };
    }
    renderReminders();
    renderTodos();
    renderGoal();
  } catch (error) {
    console.error("Could not load saved widgets:", error);
    setWidgetStatus("Could not load your saved widgets. Try refreshing the page.");
  }
}

setupWidgets();
loadWidgets();
applyBackground();

function setupSettings() {
  const panel = document.getElementById("settings-panel");
  const presetsElement = document.getElementById("presets");

  document.getElementById("settings-btn").addEventListener("click", () => {
    panel.hidden = !panel.hidden;
  });

  PRESETS.forEach((gradient) => {
    const button = document.createElement("button");
    button.className = "preset";
    button.style.backgroundImage = gradient;
    button.addEventListener("click", () => saveBackground(gradient));
    presetsElement.appendChild(button);
  });

  document.getElementById("upload").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      const dataUrl = await resizeImage(file);
      await saveBackground(`url("${dataUrl}")`);
    } catch (error) {
      console.error("Could not load image:", error);
      setWidgetStatus("Could not load that background image.");
    }
  });

  document.getElementById("reset-btn").addEventListener("click", () => {
    saveBackground("");
  });
}
setupSettings();
