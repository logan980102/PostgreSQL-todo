from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import requests
import pytz


app = Flask(__name__)

API_KEY = "0c3ab40f7d457d50856c64cebbaa68e7"
CITY = "Sancheok-dong, KR"
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

# ✅ 한글 요일 변환 함수
def get_korean_weekday():
    weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    return weekdays[datetime.now().weekday()]  # 0(월) ~ 6(일) 매핑

# ✅ 날씨 데이터 가져오기
def get_weather():
    city = "Hwaseong-si"
    country = "KR"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={API_KEY}&units=metric&lang=kr"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200:
            return None

        return {
            "description": data["weather"][0]["description"],  # 날씨 설명 (한글)
            "icon": data["weather"][0]["icon"],  # 날씨 아이콘
            "temperature": round(data["main"]["temp"]),  # 현재 온도 (반올림)
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

# ✅ 메인 페이지 라우트
@app.route("/")
def index():
    # 한국 시간(KST) 설정
    kst = pytz.timezone("Asia/Seoul")
    today = datetime.now(kst).strftime("%m월 %d일 %A")

    # 📌 날씨 데이터 가져오기
    weather = get_weather()

    return render_template("index.html", today=today, weather=weather)




# 투두리스트 조회
# 이하 기존 코드 생략

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
