from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
# 📌 DB 초기화
def init_db():
    with sqlite3.connect("todos.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit()

init_db()

# 🏠 메인 페이지
@app.route("/")
def index():
    return render_template("index.html")

# 📌 모든 투두 가져오기
@app.route("/todos")
def get_todos():
    with sqlite3.connect("todos.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, text, done FROM todos")
        todos = [{"id": row[0], "text": row[1], "done": bool(row[2])} for row in cur.fetchall()]
    return jsonify(todos)

# ➕ 할 일 추가
@app.route("/add", methods=["POST"])
def add_todo():
    data = request.json
    text = data.get("text", "").strip()
    if text:
        with sqlite3.connect("todos.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO todos (text, done) VALUES (?, ?)", (text, 0))
            conn.commit()
    return "", 204

# ✅ 완료 상태 토글
@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    with sqlite3.connect("todos.db") as conn:
        cur = conn.cursor()
        cur.execute("UPDATE todos SET done = NOT done WHERE id = ?", (todo_id,))
        conn.commit()
    return "", 204

# ❌ 삭제
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    with sqlite3.connect("todos.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
    return "", 204

# 🗑 전체 삭제
@app.route("/reset", methods=["POST"])
def reset_todos():
    with sqlite3.connect("todos.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM todos")
        conn.commit()
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
