from fastapi import FastAPI
# uvicorn main:app --reload

app = FastAPI()

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