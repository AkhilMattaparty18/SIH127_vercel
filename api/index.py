import sys
from fastapi import FastAPI, Request

app = FastAPI()

# Standard MongoDB URI
MONGO_URI = "mongodb+srv://user1:user12326@cluster0.rn7dha5.mongodb.net/?retryWrites=true&w=majority"


@app.get("/")
@app.get("/api")
def home():
    return {"status": "API is online"}


@app.post("/api/add-log")
@app.post("/add-log")
async def add_vehicle_log(request: Request):
    # Catch raw body parsing errors
    try:
        log_data = await request.json()
    except Exception as parse_err:
        return {"status": "error", "message": f"Invalid JSON payload: {str(parse_err)}"}

    # Connect to MongoDB inside the route handler
    try:
        from pymongo import MongoClient

        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        logs_col = client["traffic_system"]["vehicle_logs"]

        # Ensure vehicle_id is uppercase if provided
        if "vehicle_id" in log_data:
            log_data["vehicle_id"] = str(log_data["vehicle_id"]).upper()

        result = logs_col.insert_one(log_data)

        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": log_data,
        }
    except Exception as db_err:
        return {
            "status": "error",
            "error_type": type(db_err).__name__,
            "message": str(db_err),
            "python_version": sys.version,
        }
