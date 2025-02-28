import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 📌 환경변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# 📌 DB 연결 함수
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# 📌 DB 초기화 함수
def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)
            conn.commit()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/todos")
def get_todos():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, text, done FROM todos")
            todos = [{"id": row[0], "text": row[1], "done": row[2]} for row in cur.fetchall()]
    return jsonify(todos)

@app.route("/add", methods=["POST"])
def add_todo():
    data = request.json
    text = data.get("text", "").strip()
    if text:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO todos (text, done) VALUES (%s, %s)", (text, False))
                conn.commit()
    return "", 204

@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE todos SET done = NOT done WHERE id = %s", (todo_id,))
            conn.commit()
    return "", 204

@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
            conn.commit()
    return "", 204

@app.route("/reset", methods=["POST"])
def reset_todos():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos")
            conn.commit()
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
