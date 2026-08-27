import os
import certifi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()


def get_db_collection():
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise HTTPException(
            status_code=500,
            detail="MONGO_URI environment variable is missing on Vercel.",
        )

    client = MongoClient(
        mongo_uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000,
    )
    return client["traffic_system"]["vehicle_logs"]


class VehicleLogSchema(BaseModel):
    cam_id: str
    vehicle_id: str
    time_stamp: str


@app.get("/")
@app.get("/api")
def home():
    return {"status": "Vercel API running successfully"}


# Cover every possible route path Vercel might pass down
@app.post("/add-log")
@app.post("/add-log/")
@app.post("/api/add-log")
@app.post("/api/add-log/")
def add_vehicle_log(log: VehicleLogSchema):
    try:
        logs_col = get_db_collection()
        log_data = log.model_dump()
        log_data["vehicle_id"] = log_data["vehicle_id"].upper()

        result = logs_col.insert_one(log_data)
        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": log_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
