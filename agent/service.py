import json

import requests

from utils import settings

STUDIO_URL = settings.STUDIO_URL
X_API_KEY = settings.X_API_KEY
VALIDATION_AGENT_ID = settings.VALIDATION_AGENT_ID
PLANNER_AGENT_ID = settings.PLANNER_AGENT_ID


def chat_with_agent(user_id, agent_id, session_id, message):
    url = STUDIO_URL
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": X_API_KEY,
    }
    data = {
        "user_id": user_id,
        "agent_id": agent_id,
        "session_id": session_id,
        "message": message,
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=900)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"Other error occurred: {err}")
        return None


class AgentService:
    def validate_matrix(self, user_message, session_id, user_name):
        agent_id = VALIDATION_AGENT_ID
        response = chat_with_agent(user_name, agent_id, session_id, user_message)
        try:
            return json.loads(response)
        except:
            sanitized_output = (
                response.replace("\n", "").replace("json", "").replace("`", "")
            )
            return json.loads(sanitized_output)
        
    def create_itinerary(self, user_message, session_id, user_name):
        agent_id = PLANNER_AGENT_ID
        response = chat_with_agent(user_name, agent_id, session_id, user_message)
        return response
