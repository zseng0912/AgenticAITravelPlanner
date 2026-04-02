from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
from app.agents.workflow import app_workflow
from app.agents.state import AgentState
from app.services.serpapi_service import serpapi_service

router = APIRouter()

class TravelRequest(BaseModel):
    """
    Schema for the incoming travel planning request from the frontend.
    """
    intent: str
    departure: Optional[str] = None
    destination: str
    start_date: str
    end_date: str
    budget: float
    preferences: List[str]
    travel_type: str
    num_people: Optional[int] = 1

@router.get("/airports/search")
async def search_airports_endpoint(q: str = ""):
    """
    Endpoint for dynamic airport/city autocomplete using SerpApi.
    """
    return await serpapi_service.search_airports_dynamic(q)

@router.post("/generate-itinerary")
async def generate_itinerary(request: TravelRequest):
    """
    Main endpoint to trigger the multi-agent travel planning workflow.
    Returns a StreamingResponse (Server-Sent Events) to provide real-time status updates.
    """
    # Initialize the state object for the LangGraph workflow
    initial_state = {
        "intent": request.intent,
        "departure": request.departure or "",
        "destination": request.destination,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "budget": request.budget,
        "preferences": request.preferences,
        "travel_type": request.travel_type,
        "num_people": request.num_people or 1,
        "tasks": [],
        "budget_decomposition": {},
        "hotel_min_price": 0,
        "hotel_max_price": 0,
        "flights": [],
        "hotels": [],
        "activities": [],
        "restaurants": [],
        "itinerary_raw": "",
        "itinerary_final": {},
        "status": "understanding_request"
    }
    
    async def event_generator():
        """
        Generator function for streaming LangGraph node outputs as SSE events.
        """
        current_state = initial_state
        
        # Use the compiled LangGraph's astream method to execute nodes asynchronously
        async for output in app_workflow.astream(initial_state):
            # Each 'output' represents the state update from a specific node
            for node_name, node_output in output.items():
                # Merge the node's output into the accumulated state
                current_state.update(node_output)
                
                # Stream the current status back to the client
                yield f"data: {json.dumps({'status': current_state.get('status', node_name)})}\n\n"
        
        # Final event containing the fully structured itinerary
        final_result = {
            "status": "completed",
            "itinerary": current_state.get("itinerary_final", {})
        }
        yield f"data: {json.dumps(final_result)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
