import os
import certifi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Fetch URI from Vercel Environment Variables
MONGO_URI = os.getenv("MONGO_URI")


def get_db_collection():
    if not MONGO_URI:
        raise HTTPException(
            status_code=500, detail="MONGO_URI environment variable not set."
        )
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    return client["traffic_system"]["vehicle_logs"]


# Data structure for incoming detection requests (vehicle_count removed)
class VehicleLogSchema(BaseModel):
    cam_id: str
    vehicle_id: str
    time_stamp: str


@app.get("/")
def home():
    return {"status": "Vercel API running successfully"}


@app.post("/api/add-log")
def add_vehicle_log(log: VehicleLogSchema):
    try:
        logs_col = get_db_collection()
        log_data = log.dict()
        log_data["vehicle_id"] = log_data["vehicle_id"].upper()

        result = logs_col.insert_one(log_data)
        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": log_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
