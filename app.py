from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

app = Flask(__name__)

# 📌 PostgreSQL 연결 정보 (직접 URL 사용)
DATABASE_URL = "postgresql://todo_db_tfuv_user:5yaa9Fj4LdpKvbKZdrkTP9IPuhOiQiWm@dpg-cv0p94qj1k6c73ec6g30-a/todo_db_tfuv"

# ✅ DB 연결 함수
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)

# ✅ DB 초기화
def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    done BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS history (
                    id SERIAL PRIMARY KEY,
                    date DATE UNIQUE,
                    completed_tasks INT DEFAULT 0,
                    total_tasks INT DEFAULT 0
                );
            """)
            conn.commit()

# ✅ 투두리스트 조회
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/todos")
def get_todos():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, text, done FROM todos ORDER BY id;")
            todos = cur.fetchall()
    return jsonify([dict(todo) for todo in todos])

# ✅ 투두 추가
@app.route("/add", methods=["POST"])
def add_todo():
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Empty task"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO todos (text) VALUES (%s) RETURNING id;", (text,))
            todo_id = cur.fetchone()[0]
            conn.commit()
    
    return jsonify({"id": todo_id, "text": text, "done": False})

# ✅ 완료 상태 토글
@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE todos SET done = NOT done WHERE id = %s RETURNING done;", (todo_id,))
            updated_done = cur.fetchone()[0]
            conn.commit()
    
    return jsonify({"id": todo_id, "done": updated_done})

# ✅ 개별 삭제
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s;", (todo_id,))
            conn.commit()
    
    return jsonify({"id": todo_id})

# ✅ 전체 초기화
@app.route("/reset", methods=["POST"])
def reset_todos():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM todos;")  # 모든 투두 삭제
                conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print(f"초기화 오류: {e}")
        return jsonify({"success": False})

if __name__ == "__main__":
    init_db()  # DB 초기화 실행
    app.run(host="0.0.0.0", port=5000, debug=True)
