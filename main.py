from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

class AvailabilityRequest(BaseModel):
    checkin: str    # ISO date, e.g. "2025-08-01"
    checkout: str   # ISO date, e.g. "2025-08-05"
    room: int       # number of rooms requested
    guest: int      # number of guests

class AvailabilityResponse(BaseModel):
    available: bool
    rooms: list[str]
    message: str

app = FastAPI(title="Mock Availability API")

# Allow CORS from any origin so your React app can call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/availability", response_model=AvailabilityResponse)
def check_availability(req: AvailabilityRequest):
    """
    Dummy logic:
      - If guest count <= rooms * 2, we "have availability"
      - Otherwise, we’re fully booked.
    """
    # Parse dates just to show realistic validation
    try:
        ci = datetime.fromisoformat(req.checkin)
        co = datetime.fromisoformat(req.checkout)
        if co <= ci:
            return AvailabilityResponse(
                available=False,
                rooms=[],
                message="Checkout must be after checkin"
            )
    except ValueError:
        return AvailabilityResponse(
            available=False,
            rooms=[],
            message="Invalid date format, must be YYYY-MM-DD"
        )

    # Simple capacity check
    if req.guest <= req.room * 2:
        rooms = [f"Room #{i+1}" for i in range(req.room)]
        return AvailabilityResponse(
            available=True,
            rooms=rooms,
            message=f"{len(rooms)} rooms available"
        )
    else:
        return AvailabilityResponse(
            available=False,
            rooms=[],
            message="Not enough capacity for guests"
        )
