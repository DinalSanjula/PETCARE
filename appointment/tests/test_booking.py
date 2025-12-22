from datetime import datetime, timedelta


def test_create_booking(client):
    payload = {
        "clinic_id": 1,
        "user_id": 1,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    }

    response = client.post("/appointment/bookings", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["clinic_id"] == 1
    assert data["user_id"] == 1
    assert data["status"] == "CONFIRMED"


def test_cancel_booking(client):
    # create booking first
    payload = {
        "clinic_id": 1,
        "user_id": 1,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    }
    create_res = client.post("/appointment/bookings", json=payload)
    booking_id = create_res.json()["id"]

    response = client.post(f"/appointment/bookings/{booking_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_reschedule_booking(client):
    payload = {
        "clinic_id": 1,
        "user_id": 1,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    }
    create_res = client.post("/appointment/bookings", json=payload)
    booking_id = create_res.json()["id"]

    reschedule_payload = {
        "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(days=1, minutes=30)).isoformat()
    }

    response = client.post(
        f"/appointment/bookings/{booking_id}/reschedule",
        json=reschedule_payload
    )

    assert response.status_code == 200
    assert response.json()["status"] == "RESCHEDULED"