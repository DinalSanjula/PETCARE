📁 PETCARE

PETCARE/
│
├── app/
│   ├── main.py
│   │
│   ├── core/                  # App-wide configs & settings
│   │   ├── config.py           # env variables, settings
│   │   ├── security.py         # JWT, password hashing
│   │   └── logging.py
│   │
│   ├── database/
│   │   ├── base.py             # Declarative Base
│   │   ├── session.py          # Async DB session
│   │   └── init_db.py
│   │
│   ├── models/                 # SQLAlchemy v2 models
│   │   ├── user_model.py
│   │   ├── clinic_model.py
│   │   ├── pet_model.py
│   │   └── booking_model.py    # 👈 PET-30
│   │
│   ├── schemas/                # Pydantic v2 schemas
│   │   ├── user_schema.py
│   │   ├── clinic_schema.py
│   │   ├── pet_schema.py
│   │   └── booking_schema.py   # 👈 PET-31
│   │
│   ├── services/               # Business logic
│   │   ├── user_service.py
│   │   ├── clinic_service.py
│   │   ├── pet_service.py
│   │   └── booking_service.py  # 👈 overlap logic here
│   │
│   ├── routers/                # API routes
│   │   ├── auth_router.py
│   │   ├── user_router.py
│   │   ├── clinic_router.py
│   │   ├── pet_router.py
│   │   └── booking_router.py   # 👈 booking endpoints
│   │
│   ├── dependencies/           # FastAPI dependencies
│   │   ├── auth.py
│   │   └── db.py
│   │
│   └── utils/                  # Helpers
│       ├── datetime_utils.py
│       └── response_utils.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── test_bookings.py
│   └── test_users.py
│
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md