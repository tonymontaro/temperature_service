# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Query, HTTPException
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from db import get_db
from models import TemperatureReading as TemperatureReadingModel
from schemas import TemperatureReading, TemperatureAverageResponse
from typing import Optional
import logging

app = FastAPI()

@app.post("/temperatures", status_code=201)
def receive_temperature(
    reading: TemperatureReading,
    db: Session = Depends(get_db)
):
    """
    Store a temperature reading in the database.
    Accepts temperature data (including building, room, sensor, and a timestamp in milliseconds) and stores
    it in a database. A timescaleDB continuous aggregate is also updated in the database to speed up queries.

    Args:
        reading (TemperatureReading): The pydantic model containing temperature reading data.
        db (Session): SQLAlchemy Session dependency provided by FastAPI.

    Raises:
        HTTPException: Returns a 500 error if storing the temperature reading fails.

    Returns:
        dict: A JSON response with a success message and reading id.
    """
    try:
        reading_time = datetime.fromtimestamp(reading.timestamp / 1000.0, tz=timezone.utc)

        with db as session:
            temp_reading = TemperatureReadingModel(
                building_id=reading.buildingId,
                room_id=reading.roomId,
                sensor_id=reading.sensorId,
                temperature=reading.temperature,
                reading_time=reading_time,
            )

            session.add(temp_reading)
            session.commit()
            session.refresh(temp_reading)
            return {"message": "Success.", "id": temp_reading.id}
    except Exception as e:
        logging.error(f"Failed to store temperature reading: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store temperature reading.")

# optional TODO: convert route functions to async and use asyncpg
@app.get("/temperatures/average", response_model=TemperatureAverageResponse)
def get_temperature_average(
    building: str,
    room: str,
    db: Session = Depends(get_db),
    minutes: Optional[int] = Query(default=15, description="Calculate the average temperature over the past X minutes.")
):
    """
    Get the average temperature for a specified building and room.
    Calculates the average temperature reading over the past [minutes] value. Defaults to a 15-minute window.

    Args:
        building (str): The building identifier.
        room (str): The room identifier.
        db (Session): SQLAlchemy Session dependency provided by FastAPI.
        minutes (int, optional): How many minutes in the past to include in the average temperature calculation. Default is 15.

    Raises:
        HTTPException: Returns a 404 error if no temperature readings were found for the provided info.

    Returns:
        TemperatureAverageResponse: A Pydantic model containing:
            - buildingId (str): The requested building ID.
            - roomId (str): The requested room ID.
            - averageTemperature (float): The computed average temperature.
            - startTime (int): The start time (in milliseconds) for the calculation range.
            - endTime (int): The end time (in milliseconds) for the calculation range.
    """
    now = datetime.now(timezone.utc)
    past_x_mins = now - timedelta(minutes=minutes)

    result = TemperatureReadingModel.get_room_average_temperature(
        db, building, room, past_x_mins, now
    )

    if result is None:
        raise HTTPException(status_code=404, detail="No temperature readings found for the specified room or timeframe.")

    start_time_ms = int(past_x_mins.timestamp() * 1000)
    end_time_ms = int(now.timestamp() * 1000)

    return TemperatureAverageResponse(
        buildingId=building,
        roomId=room,
        averageTemperature=result,
        startTime=start_time_ms,
        endTime=end_time_ms
    )
