\# Task API (CRUD)



A simple Task management API built with FastAPI and PostgreSQL, running in Docker.



\## How to run (Docker)



1\. Install Docker Desktop

2\. Copy .env.example to .env and set your own password

3\. Run: docker compose up --build

4\. Open http://127.0.0.1:8000/docs



To stop: docker compose down (your data is kept).



\## Endpoints



| Method | Path | Description |

|--------|------|-------------|

| GET | / | API info |

| GET | /health | Health check |

| GET | /tasks | List all tasks |

| GET | /tasks/{id} | Get one task |

| POST | /tasks | Create a task |

| PUT | /tasks/{id} | Update a task |

| DELETE | /tasks/{id} | Delete a task |



\## Database



\- PostgreSQL 16 runs in its own container (db service)

\- Data is stored in the Docker volume pgdata, so it survives restarts

\- The app waits until the database is healthy before it starts

\- The connection string and password come from .env (gitignored). .env.example is committed as a template

\- The tasks table is created automatically by the app on startup (init\_db in main.py)



\## Architecture note (honest)



In this project the SQL queries are written directly inside the route functions in main.py. There is no separate repository layer. So moving from SQLite (Assignment 2) to Postgres meant changing main.py itself, not just swapping one file behind an interface. The endpoints (URLs) stayed the same.



\## Persistence check



1\. Started the stack with docker compose up --build

2\. Created a task ("Docker test task") with POST /tasks in Swagger UI

3\. Ran GET /tasks and saw the task (id 4)

4\. Stopped everything with Ctrl+C and docker compose down (containers removed)

5\. Ran docker compose up again

6\. Opened http://127.0.0.1:8000/tasks and all 4 tasks were still there

