import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { runInNewContext } from "node:vm";

const source = readFileSync(new URL("../newtab.js", import.meta.url), "utf8");

function createElement() {
  return {
    children: [],
    listeners: {},
    attributes: {},
    style: {},
    hidden: false,
    textContent: "",
    value: "",
    checked: false,
    addEventListener(name, callback) {
      this.listeners[name] = callback;
    },
    append(...elements) {
      this.children.push(...elements);
    },
    appendChild(element) {
      this.children.push(element);
    },
    replaceChildren(...elements) {
      this.children = [...elements];
    },
    setAttribute(name, value) {
      this.attributes[name] = value;
    },
    reset() {
      this.wasReset = true;
    },
  };
}

function createHarness({ initialStorage = {}, failWrites = false } = {}) {
  const storage = { ...initialStorage };
  const elements = new Map();
  const getElement = (id) => {
    if (!elements.has(id)) elements.set(id, createElement());
    return elements.get(id);
  };
  const fetchCalls = [];
  let nextId = 0;

  runInNewContext(source, {
    console: { error() {} },
    setInterval() {},
    document: {
      body: createElement(),
      getElementById: getElement,
      createElement,
    },
    chrome: {
      storage: {
        local: {
          async get(keys) {
            const requested = Array.isArray(keys) ? keys : [keys];
            return Object.fromEntries(requested.map((key) => [key, storage[key]]));
          },
          async set(values) {
            if (failWrites) throw new Error("Storage unavailable");
            Object.assign(storage, values);
          },
          async remove(key) {
            delete storage[key];
          },
        },
      },
    },
    crypto: {
      randomUUID() {
        nextId += 1;
        return `test-id-${nextId}`;
      },
    },
    async fetch(url) {
      fetchCalls.push(url);
      if (url !== "quotes.json") throw new Error(`Unexpected fetch: ${url}`);
      return {
        ok: true,
        async json() {
          return [{ text: "A useful quote.", author: "Example" }];
        },
      };
    },
  });

  return { elements, fetchCalls, getElement, storage };
}

async function settleStartup() {
  await new Promise((resolve) => setTimeout(resolve, 0));
}

function localDateTime(date) {
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
    + `T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

test("loads saved widgets and removes the old news cache without network calls", async () => {
  const app = createHarness({
    initialStorage: {
      reminders: [{
        id: "reminder-1",
        text: "Pay rent",
        dueAt: new Date(Date.now() - 60_000).toISOString(),
        completed: false,
      }],
      todos: [{ id: "todo-1", text: "Buy groceries", completed: false }],
      personalGoal: { title: "Run regularly", progress: 35 },
      newsCache: { fetchedOn: "2026-01-01", data: {} },
    },
  });

  await settleStartup();

  assert.equal(app.storage.newsCache, undefined);
  assert.deepEqual(app.fetchCalls, ["quotes.json"]);
  assert.match(app.getElement("reminder-list").children[0].className, /is-due/);
  assert.equal(app.getElement("todo-list").children[0].children[1].textContent, "Buy groceries");
  assert.equal(app.getElement("goal-title").value, "Run regularly");
  assert.equal(app.getElement("goal-progress-bar").value, 35);
});

test("adds and persists a reminder with a due date", async () => {
  const app = createHarness();
  await settleStartup();
  app.getElement("reminder-text").value = "Call the dentist";
  app.getElement("reminder-when").value = localDateTime(new Date(Date.now() + 3_600_000));

  await app.getElement("reminder-form").listeners.submit({ preventDefault() {} });

  assert.equal(app.storage.reminders.length, 1);
  assert.equal(app.storage.reminders[0].text, "Call the dentist");
  assert.equal(app.storage.reminders[0].dueAt, new Date(app.getElement("reminder-when").value).toISOString());
  assert.equal(app.getElement("reminder-form").wasReset, true);
  assert.match(app.getElement("reminder-list").children[0].children[1].children[1].textContent, /Upcoming/);
});

test("adds tasks, marks them complete, and deletes them", async () => {
  const app = createHarness();
  await settleStartup();
  app.getElement("todo-text").value = "Read a chapter";
  await app.getElement("todo-form").listeners.submit({ preventDefault() {} });

  assert.equal(app.storage.todos[0].text, "Read a chapter");
  assert.equal(app.getElement("todo-form").wasReset, true);

  const checkbox = app.getElement("todo-list").children[0].children[0];
  checkbox.checked = true;
  checkbox.listeners.change();
  await settleStartup();
  assert.equal(app.storage.todos[0].completed, true);

  app.getElement("todo-list").children[0].children[2].listeners.click();
  await settleStartup();
  assert.equal(app.storage.todos.length, 0);
});

test("saves, updates, and clears a personal goal", async () => {
  const app = createHarness();
  await settleStartup();
  app.getElement("goal-title").value = "Learn a language";
  app.getElement("goal-progress").value = "70";
  app.getElement("goal-progress").listeners.input();
  await app.getElement("goal-form").listeners.submit({ preventDefault() {} });

  assert.equal(app.storage.personalGoal.title, "Learn a language");
  assert.equal(app.storage.personalGoal.progress, 70);
  assert.equal(app.getElement("goal-progress-label").textContent, "70%");
  await app.getElement("goal-reset").listeners.click();
  assert.equal(app.storage.personalGoal.title, "");
  assert.equal(app.storage.personalGoal.progress, 0);
});

test("shows a visible error when widget storage fails", async () => {
  const app = createHarness({ failWrites: true });
  await settleStartup();
  app.getElement("todo-text").value = "This will not save";

  await app.getElement("todo-form").listeners.submit({ preventDefault() {} });

  assert.equal(app.storage.todos, undefined);
  assert.equal(
    app.getElement("widget-status").textContent,
    "Could not save your tasks. Please try again.",
  );
});
