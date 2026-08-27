import certifi
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Full cluster URL prevents the DNS error
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
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
        )
        logs_col = client["traffic_system"]["vehicle_logs"]

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
        return {
            "status": "error",
            "message": str(e),
        }
