from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Direct connection string with user1:user12326
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
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000,
        )
        logs_col = client["traffic_system"]["vehicle_logs"]

        log_data = {
            "cam_id": log.cam_id,
            "vehicle_id": log.vehicle_id.upper(),
            "time_stamp": log.time_stamp,
        }

        result = logs_col.insert_one(log_data)
        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": log_data,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }
