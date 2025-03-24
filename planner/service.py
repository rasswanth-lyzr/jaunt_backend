import datetime

import pandas as pd
import requests

from agent import agent_service
from planner.model import FeedbackInput, ItineraryInput, ValidationInput
from utils import settings


def get_weather(lat, lon):
    """Get weather information using OpenWeather API 2.5"""
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.WEATHER_API_KEY,
        "units": "metric",
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        return {
            "temp": weather_data.get("main", {}).get("temp"),
            "feels_like": weather_data.get("main", {}).get("feels_like"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "weather": weather_data.get("weather", [{}])[0].get("description"),
            "wind_speed": weather_data.get("wind", {}).get("speed"),
        }

    except Exception as e:
        print(f"Error getting weather: {str(e)}")
        return {}


def calculate_distance_matrix_mapbox(coordinates, mode):
    """Calculate distance matrix using Mapbox Directions API"""
    url = (
        settings.MAPBOX_DISTANCE_MATRIX_URL
        + f"{mode}/{coordinates}?annotations=distance&access_token={settings.MAPBOX_API_KEY}"
    )

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        distance_matrix = data["distances"]
        return distance_matrix
    else:
        raise Exception("Error calculating distance matrix")


def optimized_route_mapbox(coordinates, mode):
    url = (
        settings.MAPBOX_OPTIMIZED_TRIPS_URL
        + f"{mode}/{coordinates}?source=first&access_token={settings.MAPBOX_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    route = []
    for waypoint in data["waypoints"]:
        route.append(waypoint["waypoint_index"])
    return route


class PlannerService:
    def __init__(self):
        pass

    def validate_trip_constraints(self, validation_input: ValidationInput):
        # 1. Check if trip_type is one of the valid types: "walking", "cycling", "driving"
        if validation_input.trip_type.lower() not in ["walking", "cycling", "driving"]:
            raise ValueError(
                "Invalid trip type. Must be one of 'walking', 'cycling', 'driving'."
            )

        # 2. Check if the start_time is before the end_time
        if validation_input.start_time >= validation_input.end_time:
            raise ValueError("Start time must be before end time.")

        # 3. Check if starting point is in the list
        places_names = [loc.name for loc in validation_input.locations]
        starting_point = validation_input.start_location
        if starting_point not in places_names:
            raise ValueError("Starting point not found in the locations list")

        # make the starting point the first location in the list
        validation_input.locations = [
            loc for loc in validation_input.locations if loc.name == starting_point
        ] + [loc for loc in validation_input.locations if loc.name != starting_point]

        # 4. Get distance matrix
        coordinates = ";".join(
            [f"{loc.longitude},{loc.latitude}" for loc in validation_input.locations]
        )
        distance_matrix = calculate_distance_matrix_mapbox(
            coordinates, validation_input.trip_type
        )
        # distance_matrix = [
        #     [0, 2281.9, 2720.7, 3835911.2],
        #     [2281.9, 0, 1336.6, 3837670.8],
        #     [2720.7, 1336.6, 0, 3838469.2],
        #     [3835911.2, 3837670.8, 3838469.6, 0],
        # ]

        df_distance = pd.DataFrame(
            data=distance_matrix, index=places_names, columns=places_names
        )

        # 5. Get weather data
        location_weather_dict = {}
        for loc in validation_input.locations:
            weather_data = get_weather(loc.latitude, loc.longitude)
            location_weather_dict[loc.name] = weather_data

        # location_weather_dict = {
        #     "Bell of Hope": {
        #         "temp": 5.75,
        #         "feels_like": 2.71,
        #         "humidity": 92,
        #         "weather": "mist",
        #         "wind_speed": 4.12,
        #     },
        #     "Sir Winston Churchill Square": {
        #         "temp": 5.83,
        #         "feels_like": 2.81,
        #         "humidity": 91,
        #         "weather": "mist",
        #         "wind_speed": 4.12,
        #     },
        #     "New York City Marble Cemetery": {
        #         "temp": 5.75,
        #         "feels_like": 2.71,
        #         "humidity": 92,
        #         "weather": "mist",
        #         "wind_speed": 4.12,
        #     },
        #     "Private William J. Hennessy Memorial": {
        #         "temp": -6.65,
        #         "feels_like": -9.4,
        #         "humidity": 64,
        #         "weather": "scattered clouds",
        #         "wind_speed": 1.53,
        #     },
        # }

        # 6. Calculate total available time for user
        available_trip_duration = datetime.datetime.strptime(
            validation_input.start_time, "%Y-%m-%d %H:%M:%S"
        ) - datetime.datetime.strptime(validation_input.end_time, "%Y-%m-%d %H:%M:%S")
        available_hours = available_trip_duration.seconds // 3600
        available_mins = available_trip_duration.seconds % 3600 // 60

        # 7. Check if the trip is possible within the constraints
        validation_message = f"""Distance matrix (in metres): {df_distance.to_string()}, Trip mode: {validation_input.trip_type}, Starting Point: {starting_point},  Weather analysis: {location_weather_dict} , Available trip duration: {available_hours} hours and {available_mins} minutes"""
        validation_response = agent_service.validate_matrix(
            validation_message, validation_input.session_id, validation_input.user_name
        )
        # validation_response = {
        #     "status": "failure",
        #     "transportation_mode": "driving",
        #     "recommendation": "Distance from Bell of Hope, Sir Winston Churchill Square, or New York City Marble Cemetery to Private William J. Hennessy Memorial significantly exceeds typical walking limits of 50,000 meters. Consider using a car or public transport to cover this large distance.",
        # }

        # store weather, locations, distance matrix, available time in object
        self.weather = location_weather_dict
        self.locations = validation_input.locations
        self.distance_matrix = df_distance
        self.coordinates = coordinates
        self.available_time = (
            f"""{available_hours} hours and {available_mins} minutes"""
        )

        return validation_response

    def create_trip_itinerary(self, itinerary_input: ItineraryInput):
        # 1. Calculate the optimal route
        optimized_route = optimized_route_mapbox(
            self.coordinates, itinerary_input.trip_type
        )

        optimized_route_names = []
        for index in optimized_route:
            optimized_route_names.append(self.locations[index])

        # 2. Create the itinerary
        user_message = f"""Locations: {self.locations}, Distance matrix based on locations (in metres): {self.distance_matrix.to_string()}, Optimized route based on distance matrix: {optimized_route_names}, User interests: {itinerary_input.preferences}, Weather analysis: {self.weather}, Original trip mode: {itinerary_input.trip_type}, Starting Point: {itinerary_input.start_location}, Available trip duration {self.available_time}"""
        if itinerary_input.validation_output["status"] == "failure":
            user_message += f""", Trip Validation Message: {itinerary_input.validation_output["recommendation"]}"""

        created_itinerary = agent_service.create_itinerary(
            user_message, itinerary_input.session_id, itinerary_input.user_name
        )

        # 3. Return an Itinerary
        self.itinerary = created_itinerary
        return {"message": "success", "itinerary": created_itinerary}

    def update_itinerary_with_feedback(self, feedback_input: FeedbackInput):
        user_message = f"""User Feedback: {feedback_input.feedback}"""
        updated_itinerary = agent_service.create_itinerary(
            user_message, feedback_input.session_id, feedback_input.user_name
        )
        self.itinerary = updated_itinerary
        return {"message": "success", "itinerary": updated_itinerary}

    def validate_and_plan_trip(self, validation_input: ValidationInput):
        pass
