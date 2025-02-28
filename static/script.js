document.addEventListener("DOMContentLoaded", function () {
  const taskInput = document.getElementById("task-input");
  const addBtn = document.getElementById("add-btn");
  const taskList = document.getElementById("task-list");
  const resetBtn = document.getElementById("reset-btn");
  const historyList = document.getElementById("history-list"); // 기록 표시 영역

  function fetchTasks() {
    fetch("/todos")
      .then((res) => res.json())
      .then((data) => {
        taskList.innerHTML = "";
        data.forEach((todo) => addTask(todo.text, todo.done, todo.id));
      });
  }

  function fetchHistory() {
    fetch("/history")
      .then((res) => res.json())
      .then((data) => {
        historyList.innerHTML = "";
        data.forEach((record) => {
          const li = document.createElement("li");
          li.textContent = `${record.date} - 완료: ${record.completed}/${record.total}`;
          historyList.appendChild(li);
        });
      });
  }

  function addTask(text, done = false, id = null) {
    if (!text.trim()) return;
    const li = document.createElement("li");
    li.classList.toggle("done", done);
    li.innerHTML = `
          <span>${text}</span>
          <button class="toggle-btn" data-id="${id}">${
      done ? "✅" : "✔️"
    }</button>
          <button class="delete-btn" data-id="${id}">🗑️</button>
      `;

    taskList.appendChild(li);
  }

  addBtn.addEventListener("click", function () {
    const text = taskInput.value.trim();
    if (text === "") return;

    fetch("/add", {
      method: "POST",
      body: JSON.stringify({ text }),
      headers: { "Content-Type": "application/json" },
    }).then(() => {
      taskInput.value = "";
      fetchTasks();
    });
  });

  taskList.addEventListener("click", function (event) {
    const target = event.target;
    const id = target.dataset.id;

    if (target.classList.contains("toggle-btn")) {
      fetch(`/toggle/${id}`, { method: "POST" }).then(() => fetchTasks());
    } else if (target.classList.contains("delete-btn")) {
      fetch(`/delete/${id}`, { method: "POST" }).then(() => fetchTasks());
    }
  });

  resetBtn.addEventListener("click", function () {
    fetch("/reset", { method: "POST" }).then(() => {
      fetchTasks();
      fetchHistory();
    });
  });

  fetchTasks();
  fetchHistory();
});
