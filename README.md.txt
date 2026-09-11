# Task API (CRUD)

A simple Task management API built with FastAPI.

## How to run
1. Install dependencies: pip install fastapi uvicorn
2. Run server: uvicorn main:app --reload
3. Open http://127.0.0.1:8000/docs

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | / | API info |
| GET | /health | Health check |
| GET | /tasks | List all tasks |
| GET | /tasks/{id} | Get one task |
| POST | /tasks | Create a task |
| PUT | /tasks/{id} | Update a task |
| DELETE | /tasks/{id} | Delete a task |

## Example
curl -i http://127.0.0.1:8000/tasks