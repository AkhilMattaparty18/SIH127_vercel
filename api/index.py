import sys
import certifi
from fastapi import FastAPI, Request
from pymongo import MongoClient

app = FastAPI()

MONGO_URI = "mongodb+srv://user1:user12326@cluster0.rn7dha5.mongodb.net/?retryWrites=true&w=majority"

# Initialize MongoClient once at module level to reuse connection pool across warm starts
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
)
db = client["traffic_system"]
logs_col = db["vehicle_logs"]


@app.get("/")
@app.get("/api")
def home():
    return {"status": "API is online"}


@app.post("/api/add-log")
@app.post("/add-log")
async def add_vehicle_log(request: Request):
    try:
        log_data = await request.json()
    except Exception as parse_err:
        return {"status": "error", "message": f"Invalid JSON payload: {str(parse_err)}"}

    try:
        # Create a copy so PyMongo does not mutate the returned response
        document_to_insert = log_data.copy()

        if "vehicle_id" in document_to_insert:
            document_to_insert["vehicle_id"] = str(
                document_to_insert["vehicle_id"]
            ).upper()

        result = logs_col.insert_one(document_to_insert)

        # Convert _id to string before returning in JSON
        document_to_insert["_id"] = str(result.inserted_id)

        return {
            "status": "success",
            "inserted_id": str(result.inserted_id),
            "data": document_to_insert,
        }
    except Exception as db_err:
        return {
            "status": "error",
            "error_type": type(db_err).__name__,
            "message": str(db_err),
            "python_version": sys.version,
        }
