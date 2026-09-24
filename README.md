# Task API (CRUD)

A simple Task management API built with FastAPI and PostgreSQL, running in Docker.

## How to run (Docker)

1. Install Docker Desktop
2. Copy .env.example to .env and set your own password
3. Run: docker compose up --build
4. Open http://127.0.0.1:8000/docs

To stop: docker compose down (your data is kept).

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

## Database

- PostgreSQL 16 runs in its own container (db service)
- Data is stored in the Docker volume pgdata, so it survives restarts
- The app waits until the database is healthy before it starts
- The connection string and password come from .env (gitignored). .env.example is committed as a template
- The tasks table is created automatically by the app on startup (init_db in main.py)

## Architecture note (honest)

In this project the SQL queries are written directly inside the route functions in main.py. There is no separate repository layer. So moving from SQLite (Assignment 2) to Postgres meant changing main.py itself, not just swapping one file behind an interface. The endpoints (URLs) stayed the same.

## Persistence check

1. Started the stack with docker compose up --build
2. Created a task ("Docker test task") with POST /tasks in Swagger UI
3. Ran GET /tasks and saw the task (id 4)
4. Stopped everything with Ctrl+C and docker compose down (containers removed)
5. Ran docker compose up again
6. Opened http://127.0.0.1:8000/tasks and all 4 tasks were still there

## Authentication (Supabase Auth)

This project uses Supabase Auth for user signup, login, logout, and protecting routes with JWT tokens.

- `SUPABASE_URL` and `SUPABASE_KEY` are stored in `.env` (not committed)
- Auth routes:
  - `POST /auth/signup` — create a new user (email + password)
  - `POST /auth/login` — returns an `access_token` (JWT) and `refresh_token`
  - `POST /auth/logout` — requires a Bearer token, signs the user out
- Route protection:
  - `GET /public/info` — open to everyone, no token needed
  - `GET /protected/profile` — requires a valid Bearer token; returns the logged-in user's info
- Swagger UI has an "Authorize" button (top right of `/docs`) — paste the `access_token` there to test protected routes directly in the browser

### How to test auth

1. Call `POST /auth/signup` with an email and password to create a user
2. Call `POST /auth/login` with the same credentials to get an `access_token`
3. Click "Authorize" in Swagger UI and paste the token (no need to type "Bearer ", Swagger adds it)
4. Call `GET /protected/profile` — it should return the user's info
5. Call `POST /auth/logout` to sign out