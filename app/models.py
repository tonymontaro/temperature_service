from sqlalchemy import Column, Integer, String, Float, DateTime
from db import ModelBase
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime


# Room, Sensor and Building should have their own models, but I will keep it simple here without making any assumptions.
class TemperatureReading(ModelBase):
    __tablename__ = "temperature_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(String, nullable=False)
    room_id = Column(String, nullable=False)
    sensor_id = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    reading_time = Column(DateTime(timezone=True), nullable=False, primary_key=True) # Primary key for hypertable

    @staticmethod
    def get_room_average_temperature(db: Session, building: str, room: str, start_time: datetime, end_time: datetime) -> float:
        query = text("""
            SELECT AVG(avg_temp)
            FROM cagg_minute_avg
            WHERE building_id = :building
              AND room_id = :room
              AND bucket >= :start_time
              AND bucket < :end_time
        """)

        return db.execute(query, {
            "building": building,
            "room": room,
            "start_time": start_time,
            "end_time": end_time
        }).scalar()
