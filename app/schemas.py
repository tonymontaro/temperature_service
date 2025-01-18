from pydantic import BaseModel, Field
from datetime import datetime, timezone

class TemperatureReading(BaseModel):
    buildingId: str
    roomId: str
    sensorId: str
    temperature: float = Field(description="Temperature in Celsius", example=23.5)
    timestamp: int = Field(description="Epoch timestamp in milliseconds", example=int(datetime.now(timezone.utc).timestamp() * 1000))


class TemperatureAverageResponse(BaseModel):
    buildingId: str
    roomId: str
    averageTemperature: float
    startTime: int
    endTime: int
