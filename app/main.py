# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Query
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
    try:
        reading_time = datetime.fromtimestamp(reading.timestamp / 1000.0, tz=timezone.utc)

        temp_reading = TemperatureReadingModel(
            building_id=reading.buildingId,
            room_id=reading.roomId,
            sensor_id=reading.sensorId,
            temperature=reading.temperature,
            reading_time=reading_time,
        )

        db.add(temp_reading)
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to store temperature reading: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store temperature reading.")

@app.get("/temperatures/average", response_model=TemperatureAverageResponse)
def get_temperature_average(
    building: str,
    room: str,
    db: Session = Depends(get_db),
    minutes: Optional[int] = Query(default=15, description="Calculate the average temperature over the past X minutes.")
):
    now = datetime.now(timezone.utc)
    past_x_mins = now - timedelta(minutes=minutes)

    try:
        result = TemperatureReadingModel.get_room_average_temperature(
            db, building, room, past_x_mins, now
        )

        avg_temp = result if result is not None else 0.0

        start_time_ms = int(past_x_mins.timestamp() * 1000)
        end_time_ms = int(now.timestamp() * 1000)

        return TemperatureAverageResponse(
            buildingId=building,
            roomId=room,
            averageTemperature=avg_temp,
            startTime=start_time_ms,
            endTime=end_time_ms
        )
    except Exception as e:
        logging.error(f"Failed to get temperature average: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get temperature average.")
