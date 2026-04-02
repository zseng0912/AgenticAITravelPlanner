from locale import normalize
from typing import Dict, Any, List
from app.agents.state import AgentState
from app.services.serpapi_service import serpapi_service
from app.services.gemini_service import gemini_service
import json
import re

async def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Initial node in the travel planning workflow.
    Analyzes the user's intent, decomposes the budget, and sets up initial search parameters.
    """
    print("--- PLANNER NODE ---")
    
    # Calculate trip duration in days
    from datetime import datetime
    d1 = datetime.strptime(state["start_date"], "%Y-%m-%d")
    d2 = datetime.strptime(state["end_date"], "%Y-%m-%d")
    days = (d2 - d1).days + 1
    
    # Use Gemini LLM to analyze the natural language request and extract structured parameters
    analysis = await gemini_service.analyze_request({
        "intent": state["intent"],
        "destination": state["destination"],
        "days": days,
        "budget": state["budget"],
        "travel_type": state["travel_type"],
        "num_people": state["num_people"]
    })
    
    # Extract hotel price ranges and normalized destination from the analysis
    hotel_range = analysis.get("hotel_per_night_range", [200, 800])
    normalize_dest = analysis.get("destination", {})
    
    return {
        "tasks": ["flights", "hotels", "activities", "itinerary", "optimization"],
        "budget_decomposition": analysis,
        "destination": normalize_dest,
        "hotel_min_price": int(hotel_range[0]),
        "hotel_max_price": int(hotel_range[1]),
        "status": "searching_flights"
    }

async def flight_search_node(state: AgentState) -> Dict[str, Any]:
    """
    Searches for flights using SerpApi based on the destination and dates.
    """
    print("--- FLIGHT SEARCH NODE ---")
    departure = state.get("departure", "LAX")
    destination = state["destination"]["iata"]
    start_date = state["start_date"]
    end_date = state["end_date"]
    
    # Fetch round-trip flights using Google Flights engine via SerpApi
    try:
        outbound_flights = await serpapi_service.search_flights(departure, destination, start_date, end_date)
        print(f"--- ROUND-TRIP FLIGHTS DATA (JSON) ---")
        print(json.dumps(outbound_flights, indent=2))
    except Exception as e:
        print(f"Error fetching flights: {e}")
        outbound_flights = []
    
    # Round-trip results already include return info in 'legs'
    return {
        "flights": outbound_flights, 
        "return_flights": [], 
        "status": "searching_hotels"
    }

async def hotel_search_node(state: AgentState) -> Dict[str, Any]:
    """
    Searches for hotels within the specified budget range and destination.
    """
    print("--- HOTEL SEARCH NODE ---")
    destination = state.get("destination", {})
    city = destination.get("city")
    country = destination.get("country")
    location = f"{city}, {country}" if country else city
    start_date = state["start_date"]
    end_date = state["end_date"]
    min_p = state.get("hotel_min_price", 0)
    max_p = state.get("hotel_max_price", 0)
    adults = state.get("num_people", 1)
    
    # Use Google Hotels engine via SerpApi
    hotels = await serpapi_service.search_hotels(
        location, 
        start_date, 
        end_date, 
        min_price=min_p, 
        max_price=max_p, 
        adults=adults
    )
    print("--- HOTEL SEARCH DATA (JSON) ---")
    print(json.dumps(hotels, indent=2))
    return {"hotels": hotels, "status": "searching_activities"}

async def activities_node(state: AgentState) -> Dict[str, Any]:
    """
    Searches for local attractions and restaurants based on user preferences.
    """
    print("--- ACTIVITIES NODE ---")
    destination = state["destination"]
    location = f"{destination['city']}, {destination['country']}"
    preferences = state["preferences"]
    
    # Fetch both activities and restaurants using Google Local search via SerpApi
    activities = await serpapi_service.search_activities(location, preferences)
    restaurants = await serpapi_service.search_restaurants(location, preferences)
    
    print("--- ACTIVITIES SEARCH DATA (JSON) ---")
    print(json.dumps(activities, indent=2))
    print("--- RESTAURANTS SEARCH DATA (JSON) ---")
    print(json.dumps(restaurants, indent=2))
    
    return {
        "activities": activities,
        "restaurants": restaurants,
        "status": "building_itinerary"
    }

async def itinerary_builder_node(state: AgentState) -> Dict[str, Any]:
    """
    Synthesizes all gathered data into a cohesive day-by-day travel plan using Gemini.
    """
    print("--- ITINERARY BUILDER NODE ---")
    
    # Calculate trip duration
    from datetime import datetime
    d1 = datetime.strptime(state["start_date"], "%Y-%m-%d")
    d2 = datetime.strptime(state["end_date"], "%Y-%m-%d")
    days = (d2 - d1).days + 1
    
    activities = state.get("activities", [])
    restaurants = state.get("restaurants", [])
    
    # Prepare all data for the LLM to process
    data = {
        "destination": state["destination"],
        "days": days,
        "budget": state["budget"],
        "preferences": state["preferences"],
        "travel_type": state["travel_type"],
        "num_people": state.get("num_people", 1),
        "budget_decomposition": state.get("budget_decomposition", {}),
        "flights": state["flights"],
        "return_flights": state.get("return_flights", []),
        "hotels": state["hotels"],
        "activities": activities,
        "restaurants": restaurants
    }
    
    # Generate the formatted itinerary using the Gemini service
    itinerary_raw = await gemini_service.generate_itinerary(data)
    return {"itinerary_raw": itinerary_raw, "status": "optimizing_plan"}

async def optimization_node(state: AgentState) -> Dict[str, Any]:
    """
    Final node that cleans up the itinerary and ensures it's properly parsed as JSON.
    """
    print("--- OPTIMIZATION NODE ---")
    raw = state["itinerary_raw"]
    
    # Extract JSON from Markdown code blocks if present
    json_match = re.search(r'```json\n(.*?)\n```', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(1)
    
    try:
        # Convert the raw string into a structured dictionary
        final_itinerary = json.loads(raw)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        # Fallback to the raw string if parsing fails
        final_itinerary = {"raw": raw}
    
    return {"itinerary_final": final_itinerary, "status": "completed"}
