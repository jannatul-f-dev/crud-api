from fastapi import FastAPI, HTTPException, Body
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

def get_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()["count"]
    if count == 0:
        cur.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Buy milk", False))
        cur.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Clean room", True))
        cur.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Read book", False))
        conn.commit()
    cur.close()
    conn.close()

init_db()

@app.get("/")
def home():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks")
def create_task(title: str = Body(..., embed=True)):
    if not title or not title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *", (title, False))
    new_task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return dict(new_task)

@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str = Body(None), done: bool = Body(None)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    new_title = title if title is not None else row["title"]
    new_done = done if done is not None else row["done"]
    cur.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *", (new_title, new_done, task_id))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return dict(updated)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return