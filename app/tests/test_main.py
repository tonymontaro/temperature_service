import os
import time
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def sample_temperature_payload(building_id, room_id, sensor_id, temperature, timestamp=None):
    if timestamp is None:
        timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    return {
        "buildingId": building_id,
        "roomId": room_id,
        "sensorId": sensor_id,
        "temperature": temperature,
        "timestamp": timestamp
    }

def test_posts_temperature_for_a_sensor():
    payload = sample_temperature_payload("B1", "R1", "S1", 22.5)
    response = client.post("/temperatures", json=payload)
    assert response.status_code == 201

def test_raises_404_for_unknown_room():
    response = client.get(
        "/temperatures/average",
        params={"building": "UnknownB", "room": "UnknownR"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No temperature readings found for the specified room or timeframe."

def test_gets_correct_average_for_single_reading():
    building = "B2"
    room = "R2"
    sensor = "S2"
    expected_temp = 23.5

    payload = sample_temperature_payload(building, room, sensor,expected_temp)
    response = client.post("/temperatures", json=payload)
    assert response.status_code == 201

    response = client.get("/temperatures/average", params={"building": building, "room": room})
    assert response.status_code == 200
    data = response.json()
    assert round(data["averageTemperature"], 2) == round(expected_temp, 2)

def test_receive_multiple_temperatures_from_the_same_room_and_get_average():
    building = "B3"
    room = "R3"

    temps = [20.0, 22.0, 24.0]
    for i in range(len(temps)):
        temp = temps[i]
        payload = sample_temperature_payload(building, room, f"S{i}", temp)
        response = client.post("/temperatures", json=payload)
        assert response.status_code == 201
        time.sleep(0.1)

    response = client.get("/temperatures/average", params={"building": building, "room": room, "minutes": 60})
    assert response.status_code == 200
    data = response.json()
    expected_average = sum(temps) / len(temps)
    assert data["buildingId"] == building
    assert data["roomId"] == room
    assert round(data["averageTemperature"], 2) == round(expected_average, 2)
    assert isinstance(data["startTime"], int)
    assert isinstance(data["endTime"], int)



def test_missing_required_query_params():
    response = client.get("/temperatures/average", params={"room": "SomeRoom"})
    assert response.status_code == 422

    response = client.get("/temperatures/average", params={"building": "SomeBuilding"})
    assert response.status_code == 422

def test_invalid_post_payload():
    invalid_payload = {
        "buildingId": "B1",
    }
    response = client.post("/temperatures", json=invalid_payload)
    assert response.status_code == 422
