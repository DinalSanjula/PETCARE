

📘 PETCARE – Docker Development Guide



This project uses Docker to provide a consistent backend environment for all teammates.





-----------------------------------------------



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



2️⃣ Switch to testing branch



git checkout testing-branch



3️⃣ Start Docker services



docker compose up -d --build



This will:



* Build the app image



* Start PostgreSQL



* Start Uvicorn automatically







---



4️⃣ Run database migrations (IMPORTANT – only first time)



docker compose exec app alembic upgrade head





---



5️⃣ (Optional) Run tests



docker compose exec app pytest -q





---



6️⃣ Access the API



API: http://localhost:8000



Swagger Docs: http://localhost:8000/docs





✅ Setup complete.





---------------------------------------------------------------



2️⃣ Daily Development Guide



Use this every day.





---



🌅 Start of the day



docker compose up -d



That’s it.

Uvicorn + DB start automatically.





---



🔁 After pulling new code



git pull

docker compose up -d





If new migration files exist:



docker compose exec app alembic upgrade head





---



🧪 Running tests



docker compose exec app pytest -q





---



📄 View logs (Uvicorn / errors)



docker compose logs -f app



Or via Docker Desktop → Containers → petcare\_app → Logs





---



🌙 End of the day (recommended)



docker compose down



Stops:



* Uvicorn



* PostgreSQL



* Docker network









##### Important Docker Commands (Quick Reference)





🔧 Core Commands



* Start everything



docker compose up -d



* Build + start (after code changes)



docker compose up -d --build



* Stop everything



docker compose down



* Stop only the app



docker compose stop app



* Restart the app



docker compose restart app





---



🗄️ Database / Alembic



* Run migrations



docker compose exec app alembic upgrade head



* Reset database (⚠️ deletes all data)



docker compose down -v

docker compose up -d

docker compose exec app alembic upgrade head





---



🧪 Testing



* Run all tests



docker compose exec app pytest



* Run tests quietly



docker compose exec app pytest -q





---



🔍 Debugging



* Check container status



docker compose ps



* View app logs



docker compose logs app



* Follow logs live



docker compose logs -f app





---



🧠 Key Rules (IMPORTANT)



❌ Do NOT run uvicorn locally



❌ Do NOT run alembic locally



❌ Do NOT install PostgreSQL locally



✅ Always use Docker commands











