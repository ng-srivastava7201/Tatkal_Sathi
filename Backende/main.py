from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mock_irctc import search_trains, book_ticket
# uvicorn main:app --reload


app = FastAPI()


class SearchRequest(BaseModel):
    source: str
    destination: str
    date: str


class BookingRequest(BaseModel):
    train_id: str
    travel_date: str
    class_name: str
    quota: str
    seats_requested: int


@app.get("/")
def home():
    return {"message": "Tatkal Train booking backend"}


@app.get("/hello")
def hello():
    return {"message": "Hello, welcome to the Tatkal Train booking backend!"}


@app.get("/api/predict")
def predict():
    return {
        "route": "Mumbai-Delhi",
        "success_probability": 0.23,
        "predicted_seats_available": 3
    }


@app.post("/mock-irctc/search")
def search(request: SearchRequest):
    trains = search_trains(
        request.source,
        request.destination,
        request.date
    )

    return {
        "status": "success",
        "count": len(trains),
        "trains": trains
    }


@app.post("/mock-irctc/book")
def book(request: BookingRequest):
    return book_ticket(
        request.train_id,
        request.travel_date,
        request.class_name,
        request.quota,
        request.seats_requested
    )
