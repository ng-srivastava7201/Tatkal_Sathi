# Tatkal Automation Ticket booking and Tracking

A reliable Tatkal train ticket booking system that minimizes frequent user logouts, reduces failed transaction attempts during peak booking hours and provide alternate route tickets, hence improving the overall booking performance and user experience.<br>

**Important:** Tatkal Sathi works against a **self-built, simulated IRCTC-like booking backend** (`mock_irctc.py`). It never connects to the real IRCTC platform. This is an academic project built for demonstration.

## Methodology
As students from different parts of the country, we have to travel frequently between the university and our hometown. During times of emergency, we have often faced difficulties to secure seats in train through the existing booking system. After talking to our peers, we understood that it a common challenge faced by many.<br>
This common experience was the foundation of our new innovative solution to address the issues in the pre-existing booking system

## Features
 
- **Seat probability prediction**: ML model estimates the chance of getting a confirmed seat for a route, class, quota and date.
- **Alternative route ranking**: ranks nearby trains by a combined score of booking probability and distance fit.
- **Preference-based fallback**: picks the best fallback train using user-weighted preferences (probability, distance, time, station) and a hard limit on switching.
- **Mock IRCTC environment**: train search and booking simulation with realistic seat inventory and random transaction failures.
- **10:00 AM auto-trigger**: APScheduler-based automation engine with an on-demand "test trigger" from the UI.
- **User accounts**: signup/login backed by SQLite (SQLAlchemy), plus booking and automation history logs.
## Tech Stack
 
| Layer | Technology |
|---|---|
| Frontend | HTML/CSS/JS pages built with Vite (multi-page), React + Tailwind plugins configured |
| Backend | FastAPI, Uvicorn, Pydantic |
| Database | SQLite via SQLAlchemy |
| AI/ML | scikit-learn (RandomForest pipeline), pandas, joblib |
| Scheduling | APScheduler |
| Hosting | Render (Web Service for backend, Static Site for frontend) |
 
## Project Structure
 
```
Tatkal_Sathi/
├── Backende/                    # FastAPI backend
│   ├── main.py                  # API entry point (all routes)
│   ├── database.py              # SQLAlchemy models + auth/booking helpers
│   └── mock_irctc.py            # Simulated IRCTC search/booking
├── aiml/                        # Machine learning
│   ├── seat_probability.py      # Model 1: seat availability predictor
│   ├── route_rank.py            # Model 2: alternative route ranker
│   ├── preference_matcher.py    # Model 3: preference-based fallback
│   └─ ai_interface.py          # Single import surface used by the backend
├── Automation and Scheduling/   # 10:00 AM scheduler + booking simulator
│   ├── api_client.py
│   ├── automation_config.py
│   ├── automation_engine
│   |── booking_simulator
│   └── scheduler.py
├── data/
│   └── generate_tatkal_data.py  # Synthetic dataset generator
├── Frontend/                    # Vite multi-page frontend
│   ├── index.html               # Login / signup
│   ├── booking.html             # Search & book
│   ├── passenger.html, payment.html, confirm.html, status.html,
│   |── ticket.html, status.html, dashboard.html, preferences.html
│   ├── api.js                   # API helper functions
│   └── vite.config.js
└── requirements.txt
```
## Future scope of the Project
Since the project is simulation based of a real ticket booking, there is a scope for future development. After ticket generation, we do not have the couch and seat number given at this point of the project. We could also work for notification bar for the upcoming journey booked.
