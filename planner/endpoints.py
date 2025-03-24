from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

from planner import planner_service
from planner.model import FeedbackInput, ItineraryInput, ValidationInput

router = APIRouter(prefix="/planner")


@router.post("/validate-trip")
async def validate_trip(validation_input: ValidationInput = Body(...)):
    """
    Validates the input and possibility of planning a trip within the constraints.
    """
    try:
        response = planner_service.validate_trip_constraints(validation_input)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return response


@router.post("/create-itinerary")
async def create_itinerary(itinerary_input: ItineraryInput = Body(...)):
    """
    Creates an itinerary based on the validated input.
    """
    try:
        response = planner_service.create_trip_itinerary(itinerary_input)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return response


@router.post("/feedback-itinerary")
async def feedback_itinerary(feedback_input: FeedbackInput = Body(...)):
    """
    Creates an new itinerary based on user feedback.
    """
    try:
        response = planner_service.update_itinerary_with_feedback(feedback_input)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return response


# @router.post("/plan_trip")
# async def plan_trip(trip_input: TripInput = Body(...)):
#     """
#     Validates the input and possibility of planning a trip within the constraints.
#     """
#     try:
#         response = validate_and_plan_trip(trip_input)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     if response["status"] == "failure":
#         return JSONResponse(content=response, status_code=400)
#     return JSONResponse(content=response, status_code=200)
