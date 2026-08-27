import os
import certifi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# 1. Hardcode fallback or fetch env var
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://user1:user12326@cluster0.rn7dha5.mongodb.net/?appName=Cluster0",
)


def get_db_collection():
    if not MONGO_URI or "<db_password>" in MONGO_URI:
        raise HTTPException(
            status_code=500,
            detail="MONGO_URI environment variable is missing or password is still default placeholder.",
        )
    # 2. Relax SSL & set explicit server selection timeout to prevent Vercel 500 hangs
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000,
    )
    return client["traffic_system"]["vehicle_logs"]


# 3. Payload Schema (No vehicle_count)
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
        # Returns exact error back in HTTP response so you can read it directly
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
