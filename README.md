# FastAPI, ARQ + Redis

A production-ready FastAPI project for managing background task queues using [ARQ](https://github.com/samuelcolvin/arq) and Redis. This project demonstrates how to offload long-running or resource-intensive tasks from your FastAPI API to asynchronous workers, enabling scalable and reliable background job execution. It includes queue management endpoints, example producer/consumer patterns, and a modular structure for easy extension.

**Why ARQ and not Celery?**

This project uses ARQ instead of Celery because the task functions are asynchronous (`async def`). ARQ is designed for asyncio-based Python code and integrates seamlessly with async frameworks like FastAPI. In contrast, using Celery with async tasks requires additional setup and third-party libraries (such as `aio-celery`), making ARQ a simpler and more natural fit for async workloads.

## Other ARQ Features

- **Non-blocking:**
  ARQ is built using Python 3’s asyncio, allowing non-blocking job enqueuing and execution. Multiple jobs (potentially hundreds) can be run simultaneously using a pool of asyncio Tasks.

- **Powerful features:**
  Deferred execution, easy retrying of jobs, and pessimistic execution make ARQ great for critical jobs that must be completed.

- **Fast:**
  Asyncio and no forking make ARQ around 7x faster than RQ for short jobs with no I/O. With I/O, that might increase to around 40x faster. (TODO: Add benchmarks)

## Project Features

- Asynchronous background task processing with ARQ for reliable job execution.
- FastAPI endpoints to enqueue tasks (`/tasks/add`, `/tasks/divide`, `/tasks/long_call`, `/tasks/scheduled_add`) and retrieve job status (`/jobs/{job_id}`).
- Integration with Redis for robust, production-grade queue management.
- Example producer/consumer patterns:
    - `add`: Performs addition of two numbers.
    - `divide`: Performs division of two numbers.
    - `long_call`: Executes an HTTP GET request with retries.
    - `scheduled_add`: Performs addition at a scheduled time.
- Task status and result retrieval via API, checking both Redis and a persistent SQLite database for job history.
- Modular codebase with clear separation of API, tasks, database models, and configuration.
- Utilizes SQLModel for database interactions and Pydantic for data validation.
- Includes startup and shutdown events.
- Demonstrates how to schedule tasks to run at a specific time using `defer_until`.
- Implements a database model (`JobHistory`) to persist job details for auditing and monitoring.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- ARQ
- Redis (for production queue backend)
- httpx (for async HTTP calls)
- pydantic

## Installation

```bash
git clone https://github.com/davidmuraya/fastapi-arq.git
cd fastapi-arq
pip install -r requirements.txt
```

Ensure you have Redis installed and running on your machine.

Create a `.env` file in the root directory and add the following lines:

```bash
REDIS_BROKER=localhost:6379
WORKER_QUEUE=app-LyiRY47QTMd
JOBS_DB=database/jobs.db
```

## Usage

### Running the project

To run the FastAPI application with ARQ worker, follow these steps:

```bash
uvicorn main:app --reload --port 5000
```

### Running the ARQ Worker

To start the ARQ worker that processes background tasks, run the following command in a separate terminal:

```bash
arq worker.WorkerSettings
```

### Example: Enqueue an Addition Task

```bash
curl -X POST "http://localhost:5000/tasks/add" -H "Content-Type: application/json" -d "{\"x\": 5, \"y\": 10}"
```

### Example: Check Job Status

```bash
curl "http://localhost:5000/jobs/<job_id>"
```

## Project Structure

```plaintext
fastapi-arq/
├── .env                    # Environment variables (not committed)
├── .gitignore              # Specifies intentionally untracked files that Git should ignore
├── config.py               # Environment configuration loading
├── database/
│   ├── connection.py       # Database connection setup (engine, session provider)
│   ├── __init__.py
│   └── models.py           # SQLModel database table definitions (e.g., JobHistory)
├── main.py                 # FastAPI application, API endpoints
├── models.py               # Pydantic models for API requests and responses (e.g., JobStatusResponse)
├── README.md               # This file: Project documentation
├── redis_pool.py           # ARQ Redis connection pool dependency
├── requirements.txt        # Python package dependencies
├── schemas/
│   ├── __init__.py
│   └── models.py           # Pydantic schemas for data validation (e.g., JobHistoryCreate, JobHistoryRead)
├── tasks.py                # ARQ task definitions (e.g., add, divide)
├── utils/
│   ├── date_parser.py      # Utility for parsing datetime strings
│   ├── events.py           # FastAPI startup/shutdown event handlers
│   ├── __init__.py
│   ├── job_info.py         # Utility for processing ARQ job information
│   └── job_info_crud.py    # CRUD operations for the JobHistory database table
└── worker.py               # ARQ worker settings and configuration
```

## Configuration

- Configure queue backend and worker settings in `worker.py` and via environment variables (`.env` file).

## External Links

- [ARQ Documentation](https://arq-docs.helpmanual.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Redis Documentation](https://redis.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## License

MIT
