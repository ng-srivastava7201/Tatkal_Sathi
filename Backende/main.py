from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mock_irctc import search_trains, book_ticket
from fastapi.middleware.cors import CORSMiddleware
# cd Backende
# uvicorn main:app --reload

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "aiml"))

from ai_interface import predict_seat_probability, rank_alternative_routes, pick_best_fallback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

#Home
@app.get("/")
def home():
    return {"message": "Tatkal Train booking backend"}

#Test API
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

#Seat probabilty prediction
@app.post("/api/predict")
def predict(request: PredictRequest):
    return predict_seat_probability(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
    )

#Find alternative routes
@app.post("/api/alternatives")
def alternatives(request: PredictRequest):
    return rank_alternative_routes(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
    )

#Fallback option
@app.post("/api/fallback")
def fallback(request: FallbackRequest):
    return pick_best_fallback(
        request.route, request.class_name, request.quota,
        request.date, request.seats_requested,
        preferences=request.preferences,
    )

#Search trains
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


#Book ticket
@app.post("/mock-irctc/book")
def book(request: BookingRequest):
    return book_ticket(
        request.train_id,
        request.travel_date,
        request.class_name,
        request.quota,
        request.seats_requested
    )

