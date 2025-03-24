import os

from dotenv import find_dotenv, load_dotenv

from utils.settings import Settings

load_dotenv(find_dotenv())

settings = Settings(
    WEATHER_API_KEY=os.getenv("WEATHER_API_KEY"),
    MAPBOX_API_KEY=os.getenv("MAPBOX_API_KEY"),
    MAPBOX_GEOCODE_URL=os.getenv("MAPBOX_GEOCODE_URL"),
    MAPBOX_DIRECTIONS_URL=os.getenv("MAPBOX_DIRECTIONS_URL"),
    MAPBOX_DISTANCE_MATRIX_URL=os.getenv("MAPBOX_DISTANCE_MATRIX_URL"),
    STUDIO_URL=os.getenv("STUDIO_URL"),
    X_API_KEY=os.getenv("X_API_KEY"),
    PLANNER_AGENT_ID=os.getenv("PLANNER_AGENT_ID"),
    VALIDATION_AGENT_ID=os.getenv("VALIDATION_AGENT_ID"),
    MAPBOX_OPTIMIZED_TRIPS_URL=os.getenv("MAPBOX_OPTIMIZED_TRIPS_URL"),
)
