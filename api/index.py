from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

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
        # 1. Connect safely to MongoDB Atlas
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000,
        )
        logs_col = client["traffic_system"]["vehicle_logs"]

        # 2. Extract dict safely regardless of Pydantic v1 or v2 version
        log_data = {
            "cam_id": log.cam_id,
            "vehicle_id": log.vehicle_id.upper(),
            "time_stamp": log.time_stamp,
        }

        # 3. Insert record
        result = logs_col.insert_one(log_data)

        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": log_data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
