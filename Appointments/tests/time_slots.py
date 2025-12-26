def test_create_time_slot(client):
    payload = {
        "clinic_id": 1,
        "day_of_week": "Monday",
        "start_time": "09:00",
        "end_time": "12:00",
        "slot_index": 1,
        "is_active": True
    }

    response = client.post("/Appointments/slots", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["clinic_id"] == 1
    assert data["day_of_week"] == "Monday"
    assert data["start_time"] == "09:00"


def test_get_available_slots(client):
    response = client.get(
        "/Appointments/slots/1/available",
        params={"date": "2025-01-01"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)