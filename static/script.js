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
    li.innerHTML = `
          <span>${text}</span>
          <button class="toggle-btn" data-id="${id}">${
      done ? "✅" : "✔️"
    }</button>
          <button class="delete-btn" data-id="${id}">🗑️</button>
      `;
    taskList.appendChild(li);
  }

  // ✅ "추가" 버튼 클릭 또는 엔터 키 입력
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

  // ✅ "완료/삭제" 버튼 이벤트 (이벤트 위임 방식)
  taskList.addEventListener("click", function (event) {
    const target = event.target;
    const id = target.dataset.id;

    if (target.classList.contains("toggle-btn")) {
      fetch(`/toggle/${id}`, { method: "POST" }).then(() => fetchTasks());
    } else if (target.classList.contains("delete-btn")) {
      fetch(`/delete/${id}`, { method: "POST" }).then(() => fetchTasks());
    }
  });

  // 🧹 "전체 삭제" 버튼
  resetBtn.addEventListener("click", function () {
    fetch("/reset", { method: "POST" }).then(() => fetchTasks());
  });

  fetchTasks();
  fetchHistory();
});
