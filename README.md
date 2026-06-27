# AI Workflow Platform

An asynchronous LLM task-processing backend: submit a prompt over HTTP, a
background worker calls a large language model, and the result is persisted to
PostgreSQL and exposed through a status endpoint.

Built on top of the async job-queue skeleton from
[davidmuraya/fastapi-arq](https://github.com/davidmuraya/fastapi-arq); see
[Attribution](#attribution) for what I added.

Status flow: `queued → in_progress → complete | failed`

- While a job is **running**, its status lives only in Redis (`in_progress`).
- When the job **ends**, an `after_job_end` hook writes the final record to
  PostgreSQL (durable). `GET /jobs/{id}` falls back from Redis to PostgreSQL,
  so results remain queryable after the Redis result expires.

## Tech stack

- **FastAPI** — HTTP API (enqueue jobs, query status)
- **arq** — async task queue (chosen over Celery/RQ because LLM calls are
  I/O-bound; one async worker process awaits many concurrent calls instead of
  forking a process per job)
- **Redis** — arq broker + short-lived job state
- **PostgreSQL** — durable job history (`job_history` table)
- **Groq** — LLM provider via an OpenAI-compatible `/chat/completions` endpoint

## Getting started

### Prerequisites

- Python 3.13
- Redis running locally
- PostgreSQL running locally, with a database named `aiwf`

### Setup

````bash
git clone https://github.com/xiaoqinglarayuan/ai-workflow-platform.git
cd ai-workflow-platform

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

REDIS_BROKER=localhost:6379
WORKER_QUEUE=app-LyiRY47QTMd
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=                       #从 https://console.groq.com/keys 获取
LLM_MODEL=llama-3.3-70b-versatile
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/aiwf


### Environment variables (`.env`)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/aiwf
REDIS_HOST=localhost
REDIS_PORT=6379
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your_groq_api_key # get one free at https://console.groq.com/keys

LLM_MODEL=llama-3.3-70b-versatile

### Create the table
```bash
python -c "from database.models import configure; configure()"
````

### Run (two processes)

```bash
# Terminal 1 — API
uvicorn main:app --reload --port 8000

# Terminal 2 — worker
arq worker.WorkerSettings
```

Open http://127.0.0.1:8000/docs

## Usage

```bash
# Submit an LLM job
curl -X POST "http://127.0.0.1:8000/tasks/llm?prompt=Explain async in one sentence"
# -> {"job_id": "...", "message": "Job successfully queued.", "success": true}

# Poll for the result
curl http://127.0.0.1:8000/jobs/<job_id>
# -> {"status": "complete", "result": {"result": "..."}, ...}
```

## Design notes

- **Why a queue at all?** LLM calls take seconds. Handling them inside the
  request would block the API under load, so requests return a `job_id`
  immediately and the work happens in the background.
- **Why arq over RQ?** LLM calls are I/O-bound. arq is async-native and runs
  many concurrent `await`s in a single process; RQ forks a process per job.
- **Why persist to PostgreSQL?** arq stores results in Redis with a TTL, so
  results disappear after `keep_result` seconds. Writing to PostgreSQL on
  `after_job_end` makes job history durable and queryable indefinitely.

## Attribution

This project is built on the async FastAPI + arq queue skeleton from
[davidmuraya/fastapi-arq](https://github.com/davidmuraya/fastapi-arq) (MIT).

My contributions on top of the original:

- Integrated an LLM task (`llm_task`) calling Groq
- Migrated job persistence from SQLite to PostgreSQL

## License

MIT
