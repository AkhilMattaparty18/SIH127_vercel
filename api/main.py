import os
import certifi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()


# Helper function to connect cleanly inside the invocation
def get_db_collection():
    mongo_uri = os.getenv("MONGO_URI")

    # Fallback check if environment variable is missing
    if not mongo_uri:
        raise HTTPException(
            status_code=500,
            detail="MONGO_URI environment variable is missing in Vercel settings.",
        )

    try:
        client = MongoClient(
            mongo_uri,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
        )
        return client["traffic_system"]["vehicle_logs"]
    except Exception as err:
        raise HTTPException(
            status_code=500, detail=f"MongoClient initialization error: {err}"
        )


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
        log_data = log.model_dump()  # Pydantic v2 compatible
        log_data["vehicle_id"] = log_data["vehicle_id"].upper()

        result = logs_col.insert_one(log_data)
        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": log_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
