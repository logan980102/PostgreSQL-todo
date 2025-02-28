from flask import Flask, render_template, request, jsonify
import psycopg2
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date, timedelta

app = Flask(__name__)

# 데이터베이스 연결 함수
DATABASE_URL = "postgresql://todo_db_tfuv_user:5yaa9Fj4LdpKvbKZdrkTP9IPuhOiQiWm@dpg-cv0p94qj1k6c73ec6g30-a/todo_db_tfuv"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# 📌 DB 초기화
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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    completed_count INTEGER NOT NULL,
                    total_count INTEGER NOT NULL
                )
            """)
            conn.commit()

init_db()

# 📌 매일 6시 자동 초기화 및 기록 저장
def reset_todos():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 현재 날짜
            today = date.today()

            # 완료된 투두 개수
            cur.execute("SELECT COUNT(*) FROM todos WHERE done = TRUE")
            completed_count = cur.fetchone()[0]

            # 전체 투두 개수
            cur.execute("SELECT COUNT(*) FROM todos")
            total_count = cur.fetchone()[0]

            # 기록 저장
            cur.execute(
                "INSERT INTO history (date, completed_count, total_count) VALUES (%s, %s, %s)",
                (today, completed_count, total_count)
            )

            # 7일 이상 지난 기록 삭제
            seven_days_ago = today - timedelta(days=7)
            cur.execute("DELETE FROM history WHERE date < %s", (seven_days_ago,))

            # 투두리스트 초기화
            cur.execute("DELETE FROM todos")
            conn.commit()

# 스케줄러 실행
scheduler = BackgroundScheduler()
scheduler.add_job(reset_todos, 'cron', hour=6)  # 매일 오전 6시 실행
scheduler.start()

# 📌 최근 7일간의 기록 가져오기
@app.route("/history")
def get_history():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT date, completed_count, total_count FROM history
                ORDER BY date DESC LIMIT 7
            """)
            history = [{"date": str(row[0]), "completed": row[1], "total": row[2]} for row in cur.fetchall()]
    return jsonify(history)

# 📌 기존 API 유지
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
def reset_todos_manual():
    reset_todos()
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
