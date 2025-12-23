import pytest
from datetime import datetime, timedelta
import json
import base64


def get_user_id_from_token(token_data):
    """Extract user_id from JWT token payload"""
    # <!-- FIXED: Extract user_id from JWT token -->
    access_token = token_data['access_token']
    # JWT format: header.payload.signature
    payload = access_token.split('.')[1]
    # Add padding if needed
    padding = len(payload) % 4
    if padding:
        payload += '=' * (4 - padding)
    decoded = json.loads(base64.urlsafe_b64decode(payload))
    return decoded['user_id']


@pytest.mark.anyio
async def test_create_booking(async_client, clinic_token, owner_token):
    # 1. Create Clinic (using clinic_token)
    clinic_headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}
    clinic_payload = {
        "name": "Booking Vet",
        "description": "For bookings",
        "phone": "0771231234",
        "address": "Colombo",
        "profile_pic_url": None,
        "area_id": None
    }
    c_resp = await async_client.post("/clinics/", json=clinic_payload, headers=clinic_headers)
    assert c_resp.status_code == 201
    clinic_id = c_resp.json()["id"]

    # 2. Activate clinic (Assuming manually or via admin, but logic might allow if not checked?
    # Logic in booking_service doesn't check is_active of clinic, but TimeSlot logic in router might not care either.
    # However, let's just proceed.

    # 3. Create TimeSlot
    # No auth on slots endpoint?
    start_dt = datetime.utcnow() + timedelta(days=1)
    day_name = start_dt.strftime("%A")
    start_time_str = "09:00"
    end_time_str = "09:30"

    slot_payload = {
        "clinic_id": clinic_id,
        "day_of_week": day_name,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "slot_index": 1,
        "is_active": True
    }
    s_resp = await async_client.post("/appointment/slots", json=slot_payload)
    assert s_resp.status_code == 201

    # 4. Create Booking
    # <!-- FIXED: Extract user_id from JWT token -->
    user_id = get_user_id_from_token(owner_token)

    # Convert day+time to ISO
    # We used start_dt (tomorrow) and 09:00
    booking_start = datetime.combine(start_dt.date(), datetime.strptime(start_time_str, "%H:%M").time())
    booking_end = datetime.combine(start_dt.date(), datetime.strptime(end_time_str, "%H:%M").time())

    booking_payload = {
        "clinic_id": clinic_id,
        "user_id": user_id,
        "start_time": booking_start.isoformat(),
        "end_time": booking_end.isoformat()
    }

    response = await async_client.post("/appointment/bookings", json=booking_payload)
    assert response.status_code == 201

    data = response.json()
    assert data["clinic_id"] == clinic_id
    assert data["user_id"] == user_id
    assert data["status"] == "CONFIRMED"


@pytest.mark.anyio
async def test_cancel_booking(async_client, clinic_token, owner_token):
    # Setup dependencies
    clinic_headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}
    c_resp = await async_client.post("/clinics/", json={"name": "Cancel Vet", "description": "d", "phone": "0770000001",
                                                        "address": "A", "profile_pic_url": None, "area_id": None},
                                     headers=clinic_headers)
    clinic_id = c_resp.json()["id"]

    start_dt = datetime.utcnow() + timedelta(days=2)
    day_name = start_dt.strftime("%A")

    await async_client.post("/appointment/slots", json={
        "clinic_id": clinic_id,
        "day_of_week": day_name,
        "start_time": "10:00",
        "end_time": "10:30",
        "slot_index": 1,
        "is_active": True
    })

    # <!-- FIXED: Extract user_id from JWT token -->
    user_id = get_user_id_from_token(owner_token)

    booking_start = datetime.combine(start_dt.date(), datetime.strptime("10:00", "%H:%M").time())
    booking_end = datetime.combine(start_dt.date(), datetime.strptime("10:30", "%H:%M").time())

    # Create
    create_res = await async_client.post("/appointment/bookings", json={
        "clinic_id": clinic_id,
        "user_id": user_id,
        "start_time": booking_start.isoformat(),
        "end_time": booking_end.isoformat()
    })
    assert create_res.status_code == 201
    booking_id = create_res.json()["id"]

    # Cancel
    response = await async_client.post(f"/appointment/bookings/{booking_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


@pytest.mark.anyio
async def test_reschedule_booking(async_client, clinic_token, owner_token):
    # Setup
    clinic_headers = {"Authorization": f"Bearer {clinic_token['access_token']}"}
    c_resp = await async_client.post("/clinics/",
                                     json={"name": "Reschedule Vet", "description": "d", "phone": "0770000002",
                                           "address": "A", "profile_pic_url": None, "area_id": None},
                                     headers=clinic_headers)
    clinic_id = c_resp.json()["id"]

    start_dt = datetime.utcnow() + timedelta(days=3)
    day_name = start_dt.strftime("%A")

    # Slot 1
    await async_client.post("/appointment/slots", json={
        "clinic_id": clinic_id,
        "day_of_week": day_name,
        "start_time": "11:00",
        "end_time": "11:30",
        "slot_index": 1,
        "is_active": True
    })

    # Slot 2 (Target)
    await async_client.post("/appointment/slots", json={
        "clinic_id": clinic_id,
        "day_of_week": day_name,
        "start_time": "11:30",
        "end_time": "12:00",
        "slot_index": 2,
        "is_active": True
    })

    # <!-- FIXED: Extract user_id from JWT token -->
    user_id = get_user_id_from_token(owner_token)

    booking_start = datetime.combine(start_dt.date(), datetime.strptime("11:00", "%H:%M").time())
    booking_end = datetime.combine(start_dt.date(), datetime.strptime("11:30", "%H:%M").time())

    # Create Booking
    create_res = await async_client.post("/appointment/bookings", json={
        "clinic_id": clinic_id,
        "user_id": user_id,
        "start_time": booking_start.isoformat(),
        "end_time": booking_end.isoformat()
    })
    booking_id = create_res.json()["id"]

    # Reschedule to Slot 2
    new_start = datetime.combine(start_dt.date(), datetime.strptime("11:30", "%H:%M").time())
    new_end = datetime.combine(start_dt.date(), datetime.strptime("12:00", "%H:%M").time())

    response = await async_client.post(
        f"/appointment/bookings/{booking_id}/reschedule",
        json={
            "start_time": new_start.isoformat(),
            "end_time": new_end.isoformat()
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "RESCHEDULED"