# API Testing Guide

## Quick Start

1. **Start the server:**
   ```powershell
   uvicorn main:app --reload
   ```

2. **Run the test script:**
   ```powershell
   python test_api.py
   ```

## Manual Testing Methods

### Method 1: Using Python Requests (Recommended)

Create a simple Python script:

```python
import requests

# Login and get token
response = requests.post(
    "http://localhost:8000/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Use the token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/dashboard", headers=headers)
print(response.json())
```

### Method 2: Using curl in PowerShell

**Important:** In PowerShell, you need to use quotes properly and escape special characters.

```powershell
# Login
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/login" -Method Post -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}'
$token = $loginResponse.access_token

# Use token for dashboard
$headers = @{
    "Authorization" = "Bearer $token"
}
$dashboard = Invoke-RestMethod -Uri "http://localhost:8000/dashboard" -Method Get -Headers $headers
$dashboard | ConvertTo-Json
```

### Method 3: Using curl.exe (Windows)

If you have curl.exe installed:

```powershell
# Login
curl.exe -X POST "http://localhost:8000/login" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Use the token (replace YOUR_TOKEN_HERE with actual token)
curl.exe -X GET "http://localhost:8000/dashboard" -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Method 4: Using Swagger UI (Easiest!)

1. Start the server: `uvicorn main:app --reload`
2. Open browser: http://localhost:8000/docs
3. Click "Authorize" button at the top
4. Login using `/login` endpoint first to get a token
5. Copy the token and paste it in the "Authorize" dialog
6. Now you can test all endpoints directly in the browser!

## Common Endpoints

### Public Endpoints

**Register NGO:**
```python
requests.post(
    "http://localhost:8000/register",
    json={
        "username": "my_ngo",
        "email": "ngo@example.com",
        "password": "mypassword"
    }
)
```

**Login:**
```python
requests.post(
    "http://localhost:8000/login",
    json={"username": "admin", "password": "admin123"}
)
```

### Protected Endpoints (Need Token)

**Get Dashboard:**
```python
headers = {"Authorization": "Bearer YOUR_TOKEN"}
requests.get("http://localhost:8000/dashboard", headers=headers)
```

**Create Report:**
```python
headers = {"Authorization": "Bearer YOUR_TOKEN"}
requests.post(
    "http://localhost:8000/reports",
    json={
        "title": "Injured Animal",
        "description": "Found injured dog",
        "location": "Park Street"
    },
    headers=headers
)
```

**Update Report Status:**
```python
headers = {"Authorization": "Bearer YOUR_TOKEN"}
requests.patch(
    "http://localhost:8000/reports/1/status",
    json={"status": "in_progress"},
    headers=headers
)
```

## Default Admin Account

- Username: `admin`
- Password: `admin123`

## Troubleshooting

**Error: "The '<' operator is reserved for future use"**
- This happens when you paste HTTP headers directly into PowerShell
- Solution: Use `Invoke-RestMethod` or `Invoke-WebRequest` instead of raw curl syntax
- Or use the Python `requests` library

**Error: "Connection refused"**
- Make sure the server is running: `uvicorn main:app --reload`
- Check if port 8000 is available

**Error: "401 Unauthorized"**
- Make sure you're including the Authorization header
- Check that your token is valid (tokens expire after 30 minutes)
- Login again to get a new token

