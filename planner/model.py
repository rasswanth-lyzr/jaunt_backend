from typing import List

from pydantic import BaseModel


class Location(BaseModel):
    name: str
    latitude: str
    longitude: str
    priority: int


class ValidationInput(BaseModel):
    locations: List[Location]
    start_location: str
    start_time: str
    end_time: str
    preferences: str
    trip_type: str = "walking"
    session_id: str
    user_name: str


class ItineraryInput(BaseModel):
    locations: List[Location]
    start_location: str
    start_time: str
    end_time: str
    preferences: str
    trip_type: str = "walking"
    session_id: str
    user_name: str
    validation_output: dict


class FeedbackInput(BaseModel):
    feedback: str
    session_id: str
    user_name: str
