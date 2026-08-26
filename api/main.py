import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI(title="Vehicle Tracking Cloud API")

# Retrieves MongoDB Atlas connection string from Vercel Environment Variables
MONGO_URI = os.getenv("MONGO_URI")

# Reuses database connection globally across requests (maxPoolSize limits open connections)
client = MongoClient(MONGO_URI, maxPoolSize=5) if MONGO_URI else None


# Data Model matching your incoming camera JSON
class DetectionData(BaseModel):
    cam_id: str
    vehicle_id: str
    vehicle_count: int
    time_stamp: Optional[str] = None


# Endpoint 1: Receive incoming JSON logs from any camera
@app.post("/api/log_detection")
def log_vehicle(data: DetectionData):
    if not client:
        raise HTTPException(
            status_code=500, detail="Database connection string not configured."
        )
    try:
        db = client["traffic_system"]
        logs_collection = db["vehicle_logs"]

        timestamp_val = data.time_stamp or datetime.utcnow().isoformat()

        log_entry = {
            "cam_id": data.cam_id,
            "vehicle_id": data.vehicle_id,
            "vehicle_count": data.vehicle_count,
            "time_stamp": timestamp_val,
        }

        result = logs_collection.insert_one(log_entry)
        return {"status": "success", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 2: Retrieve full path history for a specific vehicle
@app.get("/api/get_path/{vehicle_id}")
def fetch_path(vehicle_id: str):
    if not client:
        raise HTTPException(
            status_code=500, detail="Database connection string not configured."
        )
    try:
        db = client["traffic_system"]
        logs_collection = db["vehicle_logs"]

        cursor = logs_collection.find({"vehicle_id": vehicle_id}).sort(
            "time_stamp", 1
        )
        trajectory = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            trajectory.append(doc)

        if not trajectory:
            raise HTTPException(
                status_code=404, detail="No vehicle logs found for this ID."
            )

        return {
            "vehicle_id": vehicle_id,
            "total_detections": len(trajectory),
            "trajectory": trajectory,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))