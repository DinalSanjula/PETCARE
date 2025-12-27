# Pet Care Welfare System

A simple FastAPI application for managing animal welfare organizations and rescue reports.

## Features

- **NGO Registration**: Organizations can register and create accounts
- **Admin Verification**: Admins can verify NGO organizations
- **Role-Based Access Control**: Different permissions for Admin and NGO users
- **JWT Authentication**: Secure token-based authentication
- **Dashboard**: View animal reports by status (new/in-progress/resolved)
- **Report Management**: Create and update animal rescue reports

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --reload
```

3. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Admin Account

- Username: `admin`
- Password: `admin123`

## API Endpoints

### Public Endpoints
- `POST /register` - Register a new NGO organization
- `POST /login` - Login and get JWT token

### NGO Endpoints (Requires NGO token)
- `GET /dashboard` - View reports by status
- `POST /reports` - Create a new animal report
- `PATCH /reports/{report_id}/status` - Update report status
- `GET /me` - Get current user info

### Admin Endpoints (Requires Admin token)
- `POST /admin/verify-ngo/{org_id}` - Verify an NGO organization
- `GET /admin/organizations` - Get all organizations

## Usage Example

1. **Register an NGO:**
```bash
POST /register
{
  "username": "ngo1",
  "email": "ngo1@example.com",
  "password": "password123"
}
```

2. **Login:**
```bash
POST /login
{
  "username": "ngo1",
  "password": "password123"
}
```
Returns: `{"access_token": "...", "token_type": "bearer"}`

3. **Use token in requests:**
Add header: `Authorization: Bearer <your_token>`

4. **Admin verifies NGO:**
```bash
POST /admin/verify-ngo/1
Authorization: Bearer <admin_token>
```

5. **Create a report:**
```bash
POST /reports
Authorization: Bearer <ngo_token>
{
  "title": "Injured Dog Found",
  "description": "Found a dog with injured leg",
  "location": "Park Street"
}
```

6. **View dashboard:**
```bash
GET /dashboard
Authorization: Bearer <ngo_token>
```

## Database

The application uses SQLite database (`petcare.db`) which is created automatically on first run.

## Learning Points

- FastAPI basics
- SQLAlchemy ORM
- JWT authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- RESTful API design

