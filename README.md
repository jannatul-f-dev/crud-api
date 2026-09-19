\# Task API (CRUD)



A simple Task management API built with FastAPI and PostgreSQL, running in Docker.



\## How to run (Docker)



1\. Install Docker Desktop

2\. Run: docker compose up --build

3\. Open http://127.0.0.1:8000/docs



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



\## Example



curl -i http://127.0.0.1:8000/tasks



\## Database



\- PostgreSQL 16 runs in its own container (db service)

\- Data is stored in the Docker volume pgdata, so it survives restarts

\- The app waits until the database is healthy before it starts

\- DATABASE\_URL is set in docker-compose.yml

