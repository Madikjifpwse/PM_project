from pydantic import BaseModel
from datetime import datetime

class IncidentCreate(BaseModel):
    title: str
    description: str
    type: str
    lat: float
    lng: float

class Incident(IncidentCreate):
    id: int
    h3_index: str
    status: str = "pending"
    created_at: datetime

class AuditLog(BaseModel):
    user_id: int
    action: str
    timestamp: datetime