from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# PostgreSQL 연결 정보
DATABASE_URL = "postgresql://todo_db_tfuv_user:5yaa9Fj4LdpKvbKZdrkTP9IPuhOiQiWm@dpg-cv0p94qj1k6c73ec6g30-a/todo_db_tfuv"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)

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

def reset_todos():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO history (date, completed_tasks, total_tasks)
                SELECT %s, COUNT(*) FILTER (WHERE done = TRUE), COUNT(*)
                FROM todos
                ON CONFLICT (date) DO NOTHING;
            """, (yesterday,))
            cur.execute("DELETE FROM todos;")
            conn.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(reset_todos, "cron", hour=6, minute=0, timezone="Asia/Seoul")
scheduler.start()

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

@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE todos SET done = NOT done WHERE id = %s RETURNING done;", (todo_id,))
            updated_done = cur.fetchone()[0]
            conn.commit()
    return jsonify({"id": todo_id, "done": updated_done})

@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s;", (todo_id,))
            conn.commit()
    return jsonify({"id": todo_id})

@app.route("/reset", methods=["POST"])
def reset():
    reset_todos()
    return jsonify({"message": "Todos reset successfully!"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)