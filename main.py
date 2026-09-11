from fastapi import FastAPI, HTTPException, Body

app = FastAPI()

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
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
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