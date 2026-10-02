from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mock_irctc import search_trains, book_ticket
# cd Backende
# uvicorn main:app --reload

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "aiml"))

from ai_interface import predict_seat_probability, rank_alternative_routes, pick_best_fallback
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

class PredictRequest(BaseModel):
    route: str
    class_name: str
    quota: str
    date: str
    seats_requested: int = 1

class FallbackRequest(PredictRequest):
    preferences: dict = {}


@app.post("/api/predict")
def predict(request: PredictRequest):
    return predict_seat_probability(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
    )

@app.post("/api/alternatives")
def alternatives(request: PredictRequest):
    return rank_alternative_routes(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
    )

@app.post("/api/fallback")
def fallback(request: FallbackRequest):
    return pick_best_fallback(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
        preferences=request.preferences,
    )


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
