from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
import h3
from datetime import datetime
from CityGuard.schemas import Incident, IncidentCreate, AuditLog
from CityGuard.db import incidents_db, audit_logs_db, users_db

app = FastAPI(title="CityGuard Institutional System")


def log_action(user_id: int, action: str):
    new_log = {"user_id": user_id, "action": action, "timestamp": datetime.utcnow()}
    audit_logs_db.append(new_log)
    print(f"AUDIT: User {user_id} performed {action}")


@app.post("/incidents", response_model=Incident)
async def create_incident(data: IncidentCreate, background_tasks: BackgroundTasks):
    h_index = h3.latlng_to_cell(data.lat, data.lng, 8)
    new_incident = {
        "id": len(incidents_db) + 1,
        **data.dict(),
        "h3_index": h_index,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    incidents_db.append(new_incident)
    background_tasks.add_task(log_action, 3, f"Created incident {new_incident['id']}")
    return new_incident


@app.get("/incidents/h3/{h3_cell}")
async def get_by_h3(h3_cell: str):
    results = [i for i in incidents_db if i["h3_index"] == h3_cell]
    return results


@app.patch("/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: int, user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user or user["role"] not in ["admin", "dispatcher"]:
        raise HTTPException(status_code=403, detail="Access denied: Only dispatchers can resolve")

    incident = next((i for i in incidents_db if i["id"] == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident["status"] = "resolved"
    log_action(user_id, f"Resolved incident {incident_id}")
    return {"message": "Incident resolved"}


@app.get("/audit")
async def get_audit(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return audit_logs_db