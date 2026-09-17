from fastapi import FastAPI, HTTPException, Body
import sqlite3

app = FastAPI()
def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    if count == 0:
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy milk", False))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Clean room", True))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Read book", False))
        conn.commit()
    conn.close()

init_db()

@app.get("/")
def home():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Clean room", "done": True},
    {"id": 3, "title": "Read book", "done": False},
]

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(row) for row in rows]
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks")
def create_task(title: str = Body(..., embed=True)):
    if not title or not title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    new_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {"id": new_id, "title": title, "done": False}
    tasks.append(new_task)
    return new_task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str = Body(None), done: bool = Body(None)):
    for task in tasks:
        if task["id"] == task_id:
            if title is not None:
                task["title"] = title
            if done is not None:
                task["done"] = done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")