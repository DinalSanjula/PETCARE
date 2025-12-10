# scripts/init_db.py
import asyncio
import importlib
from pathlib import Path
from dotenv import load_dotenv

# ensure .env loaded so db uses right DATABASE_URL
load_dotenv(dotenv_path=str(Path.cwd() / ".env"))

# import canonical engine and Base
from db import engine, Base

# list model modules that register ORM models on Base
MODEL_MODULES = [
    "app.models.user_model",
    "Clinics.models.models",
    # add any other model modules if you have them
]

def import_models():
    for mod in MODEL_MODULES:
        try:
            importlib.import_module(mod)
            print("imported", mod)
        except Exception as exc:
            print("could not import", mod, "->", exc)

async def init_db():
    import_models()
    print("Tables to create:", sorted(Base.metadata.tables.keys()))
    async with engine.begin() as conn:
        # run_sync will execute the sync create_all in the async context
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Database initialized: created tables.")

if __name__ == "__main__":
    asyncio.run(init_db())