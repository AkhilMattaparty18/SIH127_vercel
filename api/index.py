import os
import certifi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Replace <password> with your ACTUAL database password.
# If password contains '@', replace it with '%40'
MONGO_URI = "mongodb+srv://user1:user12326@cluster0.rn7dha5.mongodb.net/?retryWrites=true&w=majority"


class VehicleLogSchema(BaseModel):
    cam_id: str
    vehicle_id: str
    time_stamp: str


@app.get("/")
@app.get("/api")
def home():
    return {"status": "Vercel API running successfully"}


@app.post("/api/add-log")
@app.post("/add-log")
def add_vehicle_log(log: VehicleLogSchema):
    try:
        # Initialize connection INSIDE the function to catch errors properly
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000,
        )
        logs_col = client["traffic_system"]["vehicle_logs"]

        # Safe dictionary conversion compatible with both Pydantic v1 and v2
        log_data = (
            log.model_dump() if hasattr(log, "model_dump") else log.dict()
        )
        log_data["vehicle_id"] = log_data["vehicle_id"].upper()

        result = logs_col.insert_one(log_data)
        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": log_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
