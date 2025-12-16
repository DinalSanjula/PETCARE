

# 📘 PETCARE – Docker Development Guide 

This project uses **Docker + automatic Alembic migrations** to provide a **stable and consistent backend environment** for all teammates.

> ✅ **Alembic migrations run automatically on container startup**  
> ❌ **Never run Alembic manually**

---

## 🧠 Core Concept (READ FIRST)

- Docker databases are tied to **Docker Compose Project Name**
- NOT tied to Git branches
- NOT tied to container restarts

👉 **Each developer MUST use a unique `COMPOSE_PROJECT_NAME`**

This prevents:
- database corruption
- missing tables
- random Alembic errors

---

## 1️⃣ First-Time Setup Guide (ONCE per machine)

Follow these steps **only once** on a new machine.

---

### ✅ Prerequisites

Install:
- Git
- Docker Desktop (**must be running**)

No need to install:
- ❌ PostgreSQL
- ❌ Python locally (optional)
- ❌ Alembic locally

---

### 🚀 Initial Setup Steps

#### 1️⃣ Clone the repository

```bash
git clone <repo-url>
cd PETCARE


---

2️⃣ Checkout the working branch

git checkout testing-branch

(or main if instructed)


---

3️⃣ Create .env file (VERY IMPORTANT) - Ask me about this

Each developer must use a unique project name.

COMPOSE_PROJECT_NAME=petcare_<your_name>
DATABASE_URL=postgresql+asyncpg://test:test@db:5432/test_db
RUN_MIGRATIONS=true

Example:

COMPOSE_PROJECT_NAME=petcare_kamal


---

4️⃣ One-time cleanup (REQUIRED)

⚠️ This removes old corrupted shared databases.

docker compose down -v
docker volume prune -f


---

5️⃣ Start Docker services

docker compose up -d --build

This will automatically:

Build the app image

Start PostgreSQL

Run Alembic migrations automatically

Start Uvicorn


✅ No manual Alembic command needed


---

6️⃣ (Optional) Run tests

docker compose exec app pytest -q


---

7️⃣ Access the API

API: http://localhost:8000

Swagger Docs: http://localhost:8000/docs


✅ Setup complete


---

2️⃣ Daily Development Guide

Use this every day.


---

🌅 Start of the day

docker compose up -d

That’s it.

DB starts

Alembic runs automatically (if needed)

App starts



---

🔁 Switching branches (IMPORTANT)

❗ You do NOT reset Docker when switching branches

Correct way:

git switch main
docker compose restart app

or

git switch testing-branch
docker compose restart app

❌ NO docker compose down
❌ NO docker compose down -v
❌ NO rebuild needed


---

🔁 After pulling new code

git pull
docker compose up -d

If Dockerfile or dependencies changed:

docker compose up -d --build

✅ Alembic runs automatically if new migrations exist


---

🔁 After merging branches (IMPORTANT)

If you merge testing-branch → main:

git checkout main
git merge testing-branch
docker compose restart app

❌ No rebuild needed
❌ No DB reset needed


---

🧪 Running tests

docker compose exec app pytest -q


---

📄 View logs

docker compose logs -f app

Or via: Docker Desktop → Containers → petcare_app → Logs


---

🌙 End of the day (recommended)

docker compose down

Stops:

Uvicorn

PostgreSQL

Docker network



---

3️⃣ Reset Commands (⚠️ USE WITH CARE)

❗ Reset database (DELETES ALL DATA)

Use ONLY when:

First-time setup

Migration history is broken

Explicitly instructed by team


docker compose down -v
docker compose up -d --build

🚫 Do NOT do this daily


---

4️⃣ Important Docker Commands (Quick Reference)

🔧 Core Commands

Start everything:

docker compose up -d

Build + start (after Dockerfile / dependency changes):

docker compose up -d --build

Stop everything:

docker compose down

Restart app only:

docker compose restart app


---

🧪 Testing

Run all tests:

docker compose exec app pytest

Quiet mode:

docker compose exec app pytest -q


---

🔍 Debugging

Check container status:

docker compose ps

View app logs:

docker compose logs app

Follow logs live:

docker compose logs -f app

Check tables exist:

docker compose exec db psql -U test -d test_db -c "\dt"


---

🧠 Key Rules (VERY IMPORTANT)

❌ Do NOT run uvicorn locally
❌ Do NOT run alembic upgrade head manually
❌ Do NOT install PostgreSQL locally
❌ Do NOT share COMPOSE_PROJECT_NAME with teammates
❌ Do NOT reset DB daily

✅ Always use Docker commands
✅ Alembic runs automatically (ENTRYPOINT fixed)
✅ One person creates migrations, others only pull
✅ Branch switching = restart app, not reset DB

