📘 PETCARE – Docker Development Guide (UPDATED)

This project uses Docker + automatic Alembic migrations to provide a consistent backend environment for all teammates.

Migrations are handled automatically on container startup.


---

1️⃣ First-Time Setup Guide

Follow these steps once on a new machine.


---

✅ Prerequisites

Install:

Git

Docker Desktop (must be running)


No need to install:

❌ PostgreSQL

❌ Python locally (optional)

❌ Alembic locally



---

🚀 Initial Setup Steps

1️⃣ Clone the repository

git clone <repo-url>
cd PETCARE


---

2️⃣ Switch to testing branch

git checkout testing-branch


---

3️⃣ Create environment file

Add these to .env file

DATABASE_URL=postgresql+asyncpg://test:test@db:5432/test_db
RUN_MIGRATIONS=true


---

4️⃣ Start Docker services

docker compose up -d --build

This will automatically:

Build the app image

Start PostgreSQL

Run Alembic migrations automatically

Start Uvicorn


✅ No manual Alembic command needed


---

5️⃣ (Optional) Run tests

docker compose exec app pytest -q


---

6️⃣ Access the API

API: http://localhost:8000

Swagger Docs: http://localhost:8000/docs


✅ Setup complete.


---

2️⃣ Daily Development Guide

Use this every day.


---

🌅 Start of the day

docker compose up -d

That’s it.

DB starts

Migrations auto-run (if needed)

App starts



---

🔁 After pulling new code

git pull
docker compose up -d --build

✅ Do NOT run Alembic manually

If new migrations exist, they are applied automatically.


---

🧪 Running tests

docker compose exec app pytest -q


---

📄 View logs (Uvicorn / errors)

docker compose logs -f app

Or via Docker Desktop → Containers → petcare_app → Logs


---

🌙 End of the day (recommended)

docker compose down

Stops:

Uvicorn

PostgreSQL

Docker network



---

3️⃣ Important Docker Commands (Quick Reference)

🔧 Core Commands

Start everything


docker compose up -d

Build + start (after dependency / Docker changes)


docker compose up -d --build

Stop everything


docker compose down

Restart app only


docker compose restart app


---

🗄️ Database & Migrations

⚠️ Migrations are automatic. Do NOT run manually.

Reset database (⚠️ deletes all data)


docker compose down -v
docker compose up -d --build

Alembic will run automatically after reset.


---

🧪 Testing

Run all tests


docker compose exec app pytest

Quiet mode


docker compose exec app pytest -q


---

🔍 Debugging

Check container status


docker compose ps

View app logs


docker compose logs app

Follow logs live


docker compose logs -f app


---

🧠 Key Rules (VERY IMPORTANT)

❌ Do NOT run uvicorn locally
❌ Do NOT run alembic upgrade head manually
❌ Do NOT install PostgreSQL locally

✅ Always use Docker commands
✅ Migrations are automatic
✅ One person creates migrations, everyone else just pulls
