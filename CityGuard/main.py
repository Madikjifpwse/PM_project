from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import h3
from CityGuard import models
from CityGuard.database import engine, get_db, SessionLocal
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(models.User).first():
        db.add_all([
            models.User(id=1, username="admin", role="admin"),
            models.User(id=2, username="dispatcher", role="dispatcher"),
            models.User(id=3, username="citizen", role="citizen")
        ])
        db.commit()
    db.close()
    yield

app = FastAPI(title="CityGuard Institutional System", lifespan=lifespan)

def create_log(db: Session, user_id: int, action: str):
    log = models.AuditLog(user_id=user_id, action=action)
    db.add(log)
    db.commit()

@app.post("/incidents/")
def create_incident(title: str, lat: float, lng: float, type: str, db: Session = Depends(get_db)):
    h_idx = h3.latlng_to_cell(lat, lng, 8)
    new_inc = models.Incident(title=title, lat=lat, lng=lng, type=type, h3_index=h_idx)
    db.add(new_inc)
    db.commit()
    db.refresh(new_inc)
    return new_inc

@app.get("/incidents/h3/{h3_cell}")
def get_incidents_by_h3(h3_cell: str, db: Session = Depends(get_db)):
    return db.query(models.Incident).filter(models.Incident.h3_index == h3_cell).all()

@app.patch("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: int, user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role not in ["admin", "dispatcher"]:
        raise HTTPException(status_code=403, detail="Access denied")
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident: raise HTTPException(status_code=404, detail="Not found")
    if incident.status == "resolved":
        raise HTTPException(status_code=400, detail="Already resolved")
    incident.status = "resolved"
    db.commit()
    create_log(db, user_id, f"Resolved incident {incident_id}")
    return {"status": "success"}

@app.get("/admin/audit-logs")
def view_logs(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return db.query(models.AuditLog).all()

@app.get("/analytics/summary")
def get_analytics(db: Session = Depends(get_db)):
    incidents = db.query(models.Incident).all()
    stats = {}
    for inc in incidents:
        stats[inc.h3_index] = stats.get(inc.h3_index, 0) + 1
    return [{"h3_index": cell, "count": count} for cell, count in stats.items()]