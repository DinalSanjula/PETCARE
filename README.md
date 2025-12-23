# 📘 PETCARE – Docker Development Guide 

This project uses **Docker + automatic Alembic migrations** to provide a **stable and consistent backend environment** for all teammates.

> ✅ **Alembic migrations run automatically on container startup**  
> ❌ **Never run Alembic manually from your local machine**

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
```

---

#### 2️⃣ Checkout the working branch

```bash
git checkout staging
# (or main if instructed)
```

---

#### 3️⃣ Create .env file (VERY IMPORTANT)

Each developer must use a **unique project name**.

**Copy `.env.example` to `.env`:**
```bash
cp .env.example .env
```

**Then edit `.env` and set your unique project name:**
```bash
COMPOSE_PROJECT_NAME=petcare_<your_name>

# Example:
# COMPOSE_PROJECT_NAME=petcare_kamal
```

**Full `.env` example:**
```env
COMPOSE_PROJECT_NAME=petcare_kamal
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MINIO_SECURE=false
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=my-bucket
OPENCAGE_API_KEY=your_api_key_here
DATABASE_URL=postgresql+asyncpg://test:test@db:5432/test_db
DATABASE_URL_LOCAL=postgresql+asyncpg://test:test@localhost:5432/test_db
RUN_MIGRATIONS=true
```

⚠️ **Important:** Ask your team lead for the `OPENCAGE_API_KEY` value.

---

#### 4️⃣ One-time cleanup (REQUIRED)

⚠️ This removes old corrupted shared databases.

```bash
docker compose down -v
docker volume prune -f
```

---

#### 5️⃣ Start Docker services

```bash
docker compose up -d --build
```

This will automatically:
- Build the app image
- Start PostgreSQL
- Start MinIO
- Run Alembic migrations automatically
- Start Uvicorn

✅ **No manual Alembic command needed**

---

#### 6️⃣ Verify everything is running

```bash
# Check container status
docker compose ps

# View app logs
docker compose logs -f app

# Check database tables
docker compose exec db psql -U test -d test_db -c "\dt"
```

You should see tables like: `users`, `clinics`, `areas`, `clinic_images`, `alembic_version`

---

#### 7️⃣ (Optional) Run tests

```bash
docker compose exec app pytest -q
```

---

#### 8️⃣ Access the API

- **API:** `http://localhost:9002`
- **Swagger Docs:** `http://localhost:9002/docs`
- **MinIO Console:** `http://localhost:9001`

⚠️ **Note about ports:** If port 9002 doesn't work, see [Port Troubleshooting Guide](#-port-issues-troubleshooting)

✅ **Setup complete!**

---

## 2️⃣ Daily Development Guide

Use this every day.

---

### 🌅 Start of the day

```bash
docker compose up -d
```

That's it!
- DB starts
- Alembic runs automatically (if needed)
- App starts

---

### 🔁 Switching branches (IMPORTANT)

❗ You do NOT reset Docker when switching branches

**Correct way:**
```bash
git switch main
docker compose restart app
```

or

```bash
git switch testing-branch
docker compose restart app
```

❌ **NO** `docker compose down`  
❌ **NO** `docker compose down -v`  
❌ **NO** rebuild needed

---

### 🔁 After pulling new code

```bash
git pull
docker compose restart app
```

**If Dockerfile or requirements.txt changed:**
```bash
docker compose up -d --build
```

✅ Alembic runs automatically if new migrations exist

---

### 🔁 After merging branches (IMPORTANT)

If you merge `testing-branch` → `main`:

```bash
git checkout main
git merge testing-branch
docker compose restart app
```

❌ No rebuild needed  
❌ No DB reset needed

---

### 🧪 Running tests

```bash
# Run all tests
docker compose exec app pytest

# Quiet mode
docker compose exec app pytest -q

# Specific test file
docker compose exec app pytest tests/test_auth.py -v
```

---

### 📄 View logs

```bash
# View app logs
docker compose logs app

# Follow logs live
docker compose logs -f app

# Last 50 lines
docker compose logs --tail=50 app
```

Or via: **Docker Desktop → Containers → petcare_app → Logs**

---

### 🌙 End of the day (recommended)

```bash
docker compose down
```

Stops:
- Uvicorn
- PostgreSQL
- MinIO
- Docker network

⚠️ **Does NOT delete data** (volumes persist)

---

## 3️⃣ Database Migrations (For Developers Adding New Models)

### When you add new SQLAlchemy models:

```bash
# 1. Make sure Docker is running
docker compose up -d

# 2. Generate migration (inside Docker container)
docker compose exec app alembic revision --autogenerate -m "add new model"

# 3. Apply the migration
docker compose exec app alembic upgrade head

# 4. Verify tables exist
docker compose exec db psql -U test -d test_db -c "\dt"
```

### When you pull migrations from teammates:

```bash
git pull
docker compose restart app
# Migrations run automatically on restart
```

❌ **NEVER run** `alembic` commands from your local machine (outside Docker)  
✅ **ALWAYS use** `docker compose exec app alembic ...`

---

## 4️⃣ Reset Commands (⚠️ USE WITH CARE)

### ❗ Reset database (DELETES ALL DATA)

Use ONLY when:
- First-time setup
- Migration history is broken
- Explicitly instructed by team

```bash
docker compose down -v
docker compose up -d --build
```

🚫 **Do NOT do this daily**

---

## 5️⃣ Important Docker Commands (Quick Reference)

### 🔧 Core Commands

**Start everything:**
```bash
docker compose up -d
```

**Build + start** (after Dockerfile / dependency changes):
```bash
docker compose up -d --build
```

**Stop everything:**
```bash
docker compose down
```

**Restart app only:**
```bash
docker compose restart app
```

**Stop and remove volumes** (⚠️ DELETES DATA):
```bash
docker compose down -v
```

---

### 🔍 Debugging

**Check container status:**
```bash
docker compose ps
```

**View app logs:**
```bash
docker compose logs app
docker compose logs -f app  # Follow live
```

**Check database tables:**
```bash
docker compose exec db psql -U test -d test_db -c "\dt"
```

**Access database shell:**
```bash
docker compose exec db psql -U test -d test_db
```

**Execute commands inside app container:**
```bash
docker compose exec app python --version
docker compose exec app ls -la
```

---

### 🧹 Cleanup Commands

**Remove unused volumes:**
```bash
docker volume prune
```

**Remove unused images:**
```bash
docker image prune -a
```

**Complete cleanup** (⚠️ removes everything):
```bash
docker system prune -a --volumes
```

---

## 6️⃣ Port Issues Troubleshooting

### Current Ports:
- **API:** `http://localhost:9002`
- **PostgreSQL:** `localhost:5432` (exposed for local tools)
- **MinIO API:** `http://localhost:9000`
- **MinIO Console:** `http://localhost:9001`

### If you get "port already in use" errors:

#### Windows Users:
Port 8000 is often reserved by Windows. We use port 9002 to avoid this.

**Check reserved ports:**
```powershell
netsh interface ipv4 show excludedportrange protocol=tcp
```

**Find what's using a port:**
```powershell
netstat -ano | findstr :9002
```

**Change port if needed:**
Edit `docker-compose.yml`:
```yaml
app:
  ports:
    - "127.0.0.1:YOUR_PORT:5000"  # Change YOUR_PORT
```

For detailed troubleshooting, see: **[PORT_TROUBLESHOOTING.md](./PORT_TROUBLESHOOTING.md)**

---

## 7️⃣ Working with Requirements

### Adding new Python packages:

```bash
# 1. Add to requirements.txt manually
echo "new-package==1.0.0" >> requirements.txt

# 2. Rebuild container
docker compose up -d --build
```

### Generating clean requirements.txt:

```bash
# Activate virtual environment (if working locally)
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install pip-chill
pip install pip-chill setuptools

# Generate clean requirements
pip-chill --no-chill > requirements.txt

# Rebuild Docker
docker compose up -d --build
```

---

## 8️⃣ Common Issues & Solutions

### Issue: App container keeps restarting

**Check logs:**
```bash
docker compose logs app
```

**Common causes:**
- Database connection failed
- Missing environment variables
- Syntax error in code

**Solution:**
```bash
docker compose down
docker compose up -d --build
docker compose logs -f app
```

---

### Issue: "No such table" errors

**Cause:** Migrations not applied

**Solution:**
```bash
docker compose exec app alembic upgrade head
```

---

### Issue: Alembic migration conflicts

**Cause:** Multiple migration heads or corrupted migration history

**Solution:**
```bash
# Check current revision
docker compose exec app alembic current

# View migration history
docker compose exec app alembic history

# If broken, reset database (⚠️ DELETES DATA)
docker compose down -v
docker compose up -d --build
```

---

### Issue: "Module not found" errors

**Cause:** New dependency added but container not rebuilt

**Solution:**
```bash
docker compose up -d --build
```

---

### Issue: Changes not reflected

**Common causes:**
- File not saved
- Using volume mount but changed cached files
- Need to restart

**Solution:**
```bash
docker compose restart app
# or
docker compose up -d --build
```

---

## 🧠 Key Rules (VERY IMPORTANT)

### ❌ DO NOT:
- Run `uvicorn` locally (outside Docker)
- Run `alembic upgrade head` from your local machine
- Install PostgreSQL locally
- Share `COMPOSE_PROJECT_NAME` with teammates
- Reset DB daily with `docker compose down -v`
- Run `pip freeze > requirements.txt` (creates bloated file)

### ✅ DO:
- Always use Docker commands
- Let Alembic run automatically on startup
- Use `docker compose exec app alembic ...` for manual migrations
- Use unique `COMPOSE_PROJECT_NAME` per developer
- Branch switching = `restart app`, not reset DB
- Use `pip-chill` for clean requirements.txt
- Ask for help if something breaks!

---

## 🆘 Need Help?

1. Check the logs: `docker compose logs -f app`
2. Check container status: `docker compose ps`
3. Try restarting: `docker compose restart app`
4. Check this guide again
5. Ask the team in Slack/Discord

---

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Port Troubleshooting Guide](./PORT_TROUBLESHOOTING.md)

---

**Last Updated:** 23rd of December 2025  
**Maintained by:** Pinitha Savidya