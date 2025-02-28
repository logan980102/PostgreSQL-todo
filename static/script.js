document.addEventListener("DOMContentLoaded", function () {
  const taskInput = document.getElementById("task-input");
  const addBtn = document.getElementById("add-btn");
  const taskList = document.getElementById("task-list");
  const resetBtn = document.getElementById("reset-btn");
  const historyList = document.getElementById("history-list");

  function fetchTasks() {
    fetch("/todos")
      .then((res) => res.json())
      .then((data) => {
        taskList.innerHTML = "";
        data.forEach((todo) => addTask(todo.text, todo.done, todo.id));
      });
  }

  function addTask(text, done = false, id = null) {
    if (!text.trim()) return;
    const li = document.createElement("li");
    li.classList.toggle("done", done);
    if (done) {
      li.style.backgroundColor = "#d4f8d4"; // ✅ 연초록색 적용
    }
    li.innerHTML = `
          <span>${text}</span>
          <div class="task-buttons">
            <button class="toggle-btn" data-id="${id}">${
      done ? "✅" : "✔️"
    }</button>
            <button class="delete-btn" data-id="${id}">🗑️</button>
          </div>
      `;
    taskList.appendChild(li);
  }

  function addTaskFromInput() {
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
  }

  addBtn.addEventListener("click", addTaskFromInput);
  taskInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      addTaskFromInput();
    }
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
    fetch("/reset", { method: "POST" }).then(() => fetchTasks());
  });

  function fetchHistory() {
    fetch("/history")
      .then((res) => res.json())
      .then((data) => {
        historyList.innerHTML = "";
        data.forEach((record) => {
          const tr = document.createElement("tr");
          const progress =
            record.total_tasks > 0
              ? `${Math.round(
                  (record.completed_tasks / record.total_tasks) * 100
                )}%`
              : "0%";
          tr.innerHTML = `
                      <td>${record.date}</td>
                      <td>${record.completed_tasks}</td>
                      <td>${record.total_tasks}</td>
                      <td>${progress}</td>
                  `;
          historyList.appendChild(tr);
        });
      });
  }

  fetchTasks();
  fetchHistory();
});
