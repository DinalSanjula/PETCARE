"""
Simple script to test the Pet Care Welfare System API
Run this after starting the server with: uvicorn main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Pet Care Welfare System - API Test Script")
print("=" * 60)

# Step 1: Register a new NGO
print("\n1. Registering a new NGO...")
try:
    register_data = {
        "username": "test_ngo",
        "email": "test@ngo.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    if response.status_code == 200:
        print(f"✓ Registration successful!")
        print(f"  User: {response.json()}")
    else:
        print(f"✗ Registration failed: {response.status_code}")
        print(f"  {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Step 2: Login as NGO
print("\n2. Logging in as NGO...")
try:
    login_data = {
        "username": "test_ngo",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        ngo_token = token_data["access_token"]
        print(f"✓ Login successful!")
        print(f"  Token: {ngo_token[:50]}...")
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  {response.text}")
        ngo_token = None
except Exception as e:
    print(f"✗ Error: {e}")
    ngo_token = None

# Step 3: Login as Admin
print("\n3. Logging in as Admin...")
try:
    admin_login = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/login", json=admin_login)
    if response.status_code == 200:
        admin_token_data = response.json()
        admin_token = admin_token_data["access_token"]
        print(f"✓ Admin login successful!")
        print(f"  Token: {admin_token[:50]}...")
    else:
        print(f"✗ Admin login failed: {response.status_code}")
        print(f"  {response.text}")
        admin_token = None
except Exception as e:
    print(f"✗ Error: {e}")
    admin_token = None

# Step 4: Admin verifies NGO
if admin_token:
    print("\n4. Admin verifying NGO organization...")
    try:
        # Get all organizations
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/organizations", headers=headers)
        if response.status_code == 200:
            orgs = response.json()
            if orgs:
                org_id = orgs[0]["id"]
                print(f"  Found organization ID: {org_id}")
                
                # Verify the organization
                response = requests.post(
                    f"{BASE_URL}/admin/verify-ngo/{org_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    print(f"✓ Organization verified!")
                    print(f"  {response.json()}")
                else:
                    print(f"✗ Verification failed: {response.status_code}")
                    print(f"  {response.text}")
            else:
                print("  No organizations found")
        else:
            print(f"✗ Failed to get organizations: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

# Step 5: Create animal report (as NGO)
if ngo_token:
    print("\n5. Creating animal report...")
    try:
        headers = {"Authorization": f"Bearer {ngo_token}"}
        report_data = {
            "title": "Injured Dog Found",
            "description": "Found a dog with injured leg near Central Park",
            "location": "Central Park, Main Street"
        }
        response = requests.post(
            f"{BASE_URL}/reports",
            json=report_data,
            headers=headers
        )
        if response.status_code == 200:
            print(f"✓ Report created successfully!")
            print(f"  {json.dumps(response.json(), indent=2, default=str)}")
        else:
            print(f"✗ Report creation failed: {response.status_code}")
            print(f"  {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

# Step 6: View dashboard
if ngo_token:
    print("\n6. Viewing dashboard...")
    try:
        headers = {"Authorization": f"Bearer {ngo_token}"}
        response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
        if response.status_code == 200:
            dashboard = response.json()
            print(f"✓ Dashboard loaded!")
            print(f"  New reports: {len(dashboard['new_reports'])}")
            print(f"  In-progress reports: {len(dashboard['in_progress_reports'])}")
            print(f"  Resolved reports: {len(dashboard['resolved_reports'])}")
            
            if dashboard['new_reports']:
                print(f"\n  Latest new report:")
                print(f"    {json.dumps(dashboard['new_reports'][0], indent=4, default=str)}")
        else:
            print(f"✗ Dashboard failed: {response.status_code}")
            print(f"  {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

# Step 7: Update report status
if ngo_token:
    print("\n7. Updating report status...")
    try:
        headers = {"Authorization": f"Bearer {ngo_token}"}
        # Get dashboard to find a report
        response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
        if response.status_code == 200:
            dashboard = response.json()
            if dashboard['new_reports']:
                report_id = dashboard['new_reports'][0]['id']
                status_update = {"status": "in_progress"}
                response = requests.patch(
                    f"{BASE_URL}/reports/{report_id}/status",
                    json=status_update,
                    headers=headers
                )
                if response.status_code == 200:
                    print(f"✓ Report status updated!")
                    print(f"  {json.dumps(response.json(), indent=2, default=str)}")
                else:
                    print(f"✗ Status update failed: {response.status_code}")
                    print(f"  {response.text}")
            else:
                print("  No reports to update")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)

