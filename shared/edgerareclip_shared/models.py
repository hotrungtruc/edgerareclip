"""Shared Pydantic models."""

from pydantic import BaseModel


class AnomalyEvent(BaseModel):
    device_id: str
    score: float
    timestamp: str


class DeviceStatus(BaseModel):
    device_id: str
    online: bool
