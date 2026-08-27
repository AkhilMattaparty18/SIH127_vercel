import os
import certifi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = FastAPI()

# 1. Reuse single MongoDB client across serverless invocations
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = None


def get_collection():
    global mongo_client
    if not MONGO_URI:
        raise HTTPException(
            status_code=500, detail="MONGO_URI environment variable missing on Vercel."
        )

    if mongo_client is None:
        mongo_client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,  # 5s timeout instead of hanging
        )
    return mongo_client["traffic_system"]["vehicle_logs"]


# 2. Payload Schema
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
        logs_col = get_collection()
        log_data = log.dict()
        log_data["vehicle_id"] = log_data["vehicle_id"].upper()

        result = logs_col.insert_one(log_data)
        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": log_data,
        }
    except PyMongoError as pe:
        # Catch explicit database connection errors
        raise HTTPException(
            status_code=500, detail=f"Database Connection Error: {str(pe)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
