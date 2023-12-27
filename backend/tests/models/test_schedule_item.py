from datetime import datetime

def test_get_schedule_item(client):
    response = client.get("/schedule_item/-1")
    assert response.status_code == 404

    response = client.post("/schedule_item/", json={"venue_id": 1, "talk_id": 1, "content": "Test content 1", "start": str(datetime.now()), "end": str(datetime.now())})
    assert response.status_code == 201
    schedule_item_id = response.json["id"]

    response = client.get(f"/schedule_item/{schedule_item_id}")
    assert response.status_code == 200
    assert response.json["venue_id"] == 1


def test_creat_schedule_item(client):
    response = client.post("/schedule_item/", json={})
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 3

    response = client.post("/schedule_item/", json={"venue_id": 2, "talk_id": 2, "content": "Test content 2", "start": str(datetime.now()), "end": str(datetime.now())})
    assert response.status_code == 201
    assert response.json["venue_id"] == 2


def test_update_schedule_item(client):
    response = client.post("/schedule_item/", json={"venue_id": 3, "talk_id": 3, "content": "Test content 3", "start": str(datetime.now()), "end": str(datetime.now())})
    schedule_item_id = response.json["id"]

    response = client.patch(f"/schedule_item/{schedule_item_id}", json={"content": ""})
    assert response.json["content"] == ""


def test_delete_schedule_item(client):
    response = client.delete("/schedule_item/-1")
    assert response.status_code == 404

    response = client.post("/schedule_item/", json={"venue_id": 4, "talk_id": 4, "content": "Test content 4", "start": str(datetime.now()), "end": str(datetime.now())})
    schedule_item_id = response.json["id"]

    response = client.delete(f"/schedule_item/{schedule_item_id}")
    assert response.status_code == 204