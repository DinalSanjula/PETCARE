"""
Simple example showing how to use the Pet Care Welfare System API
This is for learning purposes - shows basic API calls
"""

import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Example 1: Register a new NGO
print("1. Registering NGO...")
register_data = {
    "username": "animal_rescue_ngo",
    "email": "rescue@example.com",
    "password": "securepassword123"
}
response = requests.post(f"{BASE_URL}/register", json=register_data)
print(f"Registration response: {response.json()}")

# Example 2: Login as NGO
print("\n2. Logging in as NGO...")
login_data = {
    "username": "animal_rescue_ngo",
    "password": "securepassword123"
}
response = requests.post(f"{BASE_URL}/login", json=login_data)
token_data = response.json()
ngo_token = token_data["access_token"]
print(f"Login successful! Token: {ngo_token[:50]}...")

# Example 3: Login as Admin (to verify NGO)
print("\n3. Logging in as Admin...")
admin_login = {
    "username": "admin",
    "password": "admin123"
}
response = requests.post(f"{BASE_URL}/login", json=admin_login)
admin_token_data = response.json()
admin_token = admin_token_data["access_token"]
print(f"Admin login successful!")

# Example 4: Admin verifies NGO (get org_id from /admin/organizations first)
print("\n4. Getting all organizations...")
headers = {"Authorization": f"Bearer {admin_token}"}
response = requests.get(f"{BASE_URL}/admin/organizations", headers=headers)
orgs = response.json()
print(f"Organizations: {orgs}")
if orgs:
    org_id = orgs[0]["id"]
    print(f"\n5. Verifying organization {org_id}...")
    response = requests.post(f"{BASE_URL}/admin/verify-ngo/{org_id}", headers=headers)
    print(f"Verification response: {response.json()}")

# Example 5: Create an animal report (as NGO)
print("\n6. Creating animal report...")
ngo_headers = {"Authorization": f"Bearer {ngo_token}"}
report_data = {
    "title": "Injured Dog Found",
    "description": "Found a dog with injured leg near the park",
    "location": "Central Park, Main Street"
}
response = requests.post(f"{BASE_URL}/reports", json=report_data, headers=ngo_headers)
print(f"Report created: {response.json()}")

# Example 6: View dashboard
print("\n7. Viewing dashboard...")
response = requests.get(f"{BASE_URL}/dashboard", headers=ngo_headers)
dashboard = response.json()
print(f"New reports: {len(dashboard['new_reports'])}")
print(f"In-progress reports: {len(dashboard['in_progress_reports'])}")
print(f"Resolved reports: {len(dashboard['resolved_reports'])}")

# Example 7: Update report status
if dashboard['new_reports']:
    report_id = dashboard['new_reports'][0]['id']
    print(f"\n8. Updating report {report_id} status to 'in_progress'...")
    status_update = {"status": "in_progress"}
    response = requests.patch(
        f"{BASE_URL}/reports/{report_id}/status",
        json=status_update,
        headers=ngo_headers
    )
    print(f"Status updated: {response.json()}")

print("\n\nExample completed!")

