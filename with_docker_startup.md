
---

# 📘 PETCARE – Docker Development Guide

This project uses **Docker + automatic Alembic migrations** to provide a **stable, predictable, and team-safe backend environment**.

> ✅ Alembic migrations run automatically on container startup  
> ❌ Never run Alembic manually  

---

## 🧠 Core Concept (READ FIRST – VERY IMPORTANT)

- Docker databases are tied to the **Docker Compose Project Name**
- ❌ NOT tied to Git branches
- ❌ NOT tied to container restarts

👉 **Each developer MUST use a unique `COMPOSE_PROJECT_NAME`**

This prevents:
- database corruption
- missing tables
- random Alembic errors
- cross-branch DB conflicts

---

## 1️⃣ First-Time Setup Guide (ONCE per machine)

Follow these steps **only once** on a new machine.

---

### ✅ Prerequisites

Install:
- Git
- Docker Desktop (**must be running**)

No need to install:
- ❌ PostgreSQL locally
- ❌ Alembic locally
- ❌ Python locally (optional)

---

### 🚀 Initial Setup Steps

#### 1️⃣ Clone the repository

```bash
git clone <repo-url>
cd PETCARE


---

2️⃣ Checkout the working branch

git checkout staging

(or main if instructed)


---

3️⃣ Create .env file (VERY IMPORTANT)

Each developer must use a unique project name.

COMPOSE_PROJECT_NAME=petcare_<your_name>
DATABASE_URL=postgresql+asyncpg://test:test@db:5432/test_db
RUN_MIGRATIONS=true

Example:

COMPOSE_PROJECT_NAME=petcare_kamal

⚠️ If RUN_MIGRATIONS is missing or false, database tables will NOT be created.


---

4️⃣ One-time cleanup (REQUIRED)

⚠️ This removes old corrupted/shared databases.

docker compose down -v
docker volume prune -f


---

5️⃣ Start Docker services

docker compose up -d --build

This automatically:

Builds the app image

Starts PostgreSQL

Runs Alembic migrations

Starts Uvicorn

Starts MinIO


✅ No manual Alembic commands needed


---

6️⃣ (Optional) Run tests

docker compose exec app pytest -q


---

7️⃣ Access the API

API: http://localhost:8000

Swagger Docs: http://localhost:8000/docs


✅ Setup complete


---
---
---

2️⃣ Daily Development Guide

Use this every day.


---

🌅 Start of the day

docker compose up -d

That’s it.

DB starts

App starts

Alembic runs automatically if needed



---

🔁 Switching branches (IMPORTANT)

❗ DO NOT reset Docker when switching branches

Correct way:

git switch main
docker compose restart app

or

git switch staging
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

🔁 After merging branches

Example: testing-branch → main

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

Or via Docker Desktop: Containers → petcare_app → Logs


---

🌙 End of the day (recommended)

docker compose down

Stops:

Uvicorn

PostgreSQL

Docker network



---

3️⃣ Docker Compose Changes (IMPORTANT)

⚠️ If docker-compose.yml is edited (services, ports, env, volumes):

git pull
docker compose down
docker compose up -d --build

This is required ONLY when the compose file changes.


---

4️⃣ Reset Commands (⚠️ USE WITH CARE)

❗ Reset database (DELETES ALL DATA)

Use ONLY when:

First-time setup

Migration history is broken

Explicitly instructed by the team


docker compose down -v
docker compose up -d --build

🚫 Do NOT do this daily


---

5️⃣ MinIO (Object Storage)

MinIO runs automatically via Docker Compose.

Access:

Console: http://localhost:9001

API: http://localhost:9000


Credentials:

Username: minioadmin

Password: minioadmin


⚠️ Inside backend code:

❌ Do NOT use localhost

✅ Use minio:9000



---

6️⃣ Quick Health Check (When Something Feels Broken)

docker compose ps
docker compose exec db psql -U test -d test_db -c "\dt"
docker compose exec app printenv DATABASE_URL
docker compose logs -f app


---

🏆 Key Rules (READ THIS IF NOTHING ELSE)

❌ Do NOT run Uvicorn locally
❌ Do NOT run Alembic manually
❌ Do NOT install PostgreSQL locally
❌ Do NOT share COMPOSE_PROJECT_NAME
❌ Do NOT reset DB daily

✅ Always use Docker commands
✅ Alembic runs automatically
✅ One person creates migrations, others only pull
✅ Branch switch = restart app
✅ Compose change = rebuild
✅ DB reset = last resort


---

If in doubt → ask before resetting the database.

---
