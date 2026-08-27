import certifi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Replace <password> with your actual MongoDB Atlas password.
# Special characters in passwords must be URL-encoded (e.g., '@' -> '%40').
MONGO_URI = "mongodb+srv://user1:<password>@cluster0.rn7dha5.mongodb.net/?retryWrites=true&w=majority"


def get_db_collection():
    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000,
        )
        return client["traffic_system"]["vehicle_logs"]
    except Exception as err:
        raise HTTPException(
            status_code=500, detail=f"Mongo Client Error: {str(err)}"
        )


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
