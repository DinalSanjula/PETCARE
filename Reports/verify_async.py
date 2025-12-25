import asyncio
import httpx

BASE_URL = "http://localhost:8004"

async def verify_api():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print("Testing Root...")
        response = await client.get("/")
        print(response.json())
        assert response.status_code == 200

        print("\nTesting Create Report (Form Data)...")
        report_data = {
            "animal_type": "dog",
            "condition": "injured",
            "description": "Dog hit by vehicle, bleeding leg",
            "address": "Near Kurunegala clock tower",
            "contact_phone": "0771234567"
        }
        response = await client.post("/reports/", data=report_data)
        print(response.json())
        assert response.status_code == 201
        report_id = response.json()["id"]

        print("\nTesting Create Report with Image (Form Data)...")
        combined_data = {
            "animal_type": "cat",
            "condition": "sick",
            "description": "Stray cat looking very weak",
            "address": "Kandy road",
            "contact_phone": "0779876543"
        }
        files = {'image': ('test_cat.jpg', b'fake cat image content', 'image/jpeg')}
        response = await client.post("/reports/", data=combined_data, files=files)
        print(response.json())
        assert response.status_code == 201
        combined_report_id = response.json()["id"]

        print(f"\nTesting Upload Image for {report_id}...")
        image_files = {'file': ('test_image.jpg', b'fake image content', 'image/jpeg')}
        response = await client.post(f"/reports/{report_id}/images", files=image_files)
        print(response.json())
        assert response.status_code == 201

        print(f"\nTesting Add Note for {report_id}...")
        note_data = {"note": "Ambulance dispatched"}
        response = await client.post(f"/reports/{report_id}/notes", json=note_data)
        print(response.json())
        assert response.status_code == 201

        print("\nTesting List Reports...")
        response = await client.get("/reports/")
        reports = response.json()
        print(f"Found {len(reports)} reports")
        assert response.status_code == 200
        assert any(r["id"] == report_id for r in reports)

        print(f"\nTesting Get Report {report_id}...")
        response = await client.get(f"/reports/{report_id}")
        print(response.json())
        assert response.status_code == 200
        assert response.json()["id"] == report_id

        print(f"\nTesting Get Report Notes {report_id}...")
        response = await client.get(f"/reports/{report_id}/notes")
        print(response.json())
        assert response.status_code == 200
        assert len(response.json()) > 0

        print(f"\nTesting Update Details for {report_id}...")
        update_data = {
            "description": "Dog hit by vehicle, bleeding leg - UPDATED: Animal is now stable",
            "condition": "stable"
        }
        response = await client.patch(f"/reports/{report_id}", json=update_data)
        print(response.json())
        assert response.status_code == 200
        assert response.json()["condition"] == "stable"

        print(f"\nTesting Update Status for {report_id}...")
        status_update = {"status": "IN_PROGRESS"}
        response = await client.patch(f"/reports/{report_id}/status", json=status_update)
        print(response.json())
        assert response.status_code == 200
        assert response.json()["status"] == "IN_PROGRESS"

        print("\nTesting Get Stats...")
        response = await client.get("/reports/stats/overview")
        print(response.json())
        assert response.status_code == 200
        assert "IN_PROGRESS" in response.json()

        print(f"\nTesting Delete Report {report_id}...")
        response = await client.delete(f"/reports/{report_id}")
        assert response.status_code == 204
        
        response = await client.get(f"/reports/{report_id}")
        assert response.status_code == 404

        print("\nAll tests passed!")

if __name__ == "__main__":
    asyncio.run(verify_api())
