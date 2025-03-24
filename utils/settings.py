from dataclasses import dataclass


@dataclass
class Settings:
    """
    Settings class for the application
    """

    WEATHER_API_KEY: str
    MAPBOX_GEOCODE_URL: str
    MAPBOX_DIRECTIONS_URL: str
    MAPBOX_DISTANCE_MATRIX_URL: str
    MAPBOX_OPTIMIZED_TRIPS_URL: str
    STUDIO_URL: str
    X_API_KEY: str
    PLANNER_AGENT_ID: str
    VALIDATION_AGENT_ID: str
    MAPBOX_API_KEY: str
