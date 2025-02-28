const taskInput = document.getElementById("task-input");
const addBtn = document.getElementById("add-btn");
const taskList = document.getElementById("task-list");

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
      <div class="button-group">
        <button class="toggle-btn" data-id="${id}">${done ? "✅" : "✔"}</button>
        <button class="delete-btn" data-id="${id}">🗑️</button>
      </div>
  `;
  taskList.appendChild(li);
}

fetchTasks();
