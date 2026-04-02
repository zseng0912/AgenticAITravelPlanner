import pytest
from unittest.mock import AsyncMock, patch
from app.agents.nodes import (
    planner_node,
    flight_search_node,
    hotel_search_node,
    activities_node,
    itinerary_builder_node
)

@pytest.mark.asyncio
@patch("app.services.gemini_service.GeminiService.analyze_request", new_callable=AsyncMock)
async def test_planner_node(mock_analyze):
    mock_analyze.return_value = {
        "destination": {"iata": "NRT", "city": "Tokyo", "country": "Japan"},
        "hotel_per_night_range": [300, 600]
    }
    
    state = {
        "intent": "trip to tokyo",
        "destination": "Tokyo",
        "start_date": "2024-05-01",
        "end_date": "2024-05-05",
        "budget": 5000,
        "travel_type": "standard",
        "num_people": 2
    }
    
    result = await planner_node(state)
    
    assert "tasks" in result
    assert result["destination"]["iata"] == "NRT"
    assert result["hotel_min_price"] == 300
    assert result["status"] == "searching_flights"

@pytest.mark.asyncio
@patch("app.services.serpapi_service.SerpAPIService.search_flights", new_callable=AsyncMock)
async def test_flight_search_node(mock_search):
    mock_search.return_value = [{"airline": "ANA", "price": 1000}]
    
    state = {
        "departure": "LAX",
        "destination": {"iata": "NRT"},
        "start_date": "2024-05-01",
        "end_date": "2024-05-05"
    }
    
    result = await flight_search_node(state)
    
    assert len(result["flights"]) == 1
    assert result["status"] == "searching_hotels"

@pytest.mark.asyncio
@patch("app.services.serpapi_service.SerpAPIService.search_hotels", new_callable=AsyncMock)
async def test_hotel_search_node(mock_search):
    mock_search.return_value = [{"name": "Hotel A", "price": "RM 500"}]
    
    state = {
        "destination": {"city": "Tokyo", "country": "Japan"},
        "start_date": "2024-05-01",
        "end_date": "2024-05-05",
        "hotel_min_price": 300,
        "hotel_max_price": 600,
        "num_people": 2
    }
    
    result = await hotel_search_node(state)
    
    assert len(result["hotels"]) == 1
    assert result["status"] == "searching_activities"

@pytest.mark.asyncio
@patch("app.services.serpapi_service.SerpAPIService.search_activities", new_callable=AsyncMock)
@patch("app.services.serpapi_service.SerpAPIService.search_restaurants", new_callable=AsyncMock)
async def test_activities_node(mock_search_restaurants, mock_search_activities):
    mock_search_activities.return_value = [{"name": "Activity 1"}]
    mock_search_restaurants.return_value = [{"name": "Restaurant 1"}]
    
    state = {
        "destination": {"city": "Tokyo", "country": "Japan"},
        "preferences": ["sushi"]
    }
    
    result = await activities_node(state)
    
    assert len(result["activities"]) == 1
    assert len(result["restaurants"]) == 1
    assert result["status"] == "building_itinerary"

@pytest.mark.asyncio
@patch("app.services.gemini_service.GeminiService.generate_itinerary", new_callable=AsyncMock)
async def test_itinerary_builder_node(mock_generate):
    mock_generate.return_value = "```json\n{\"days\": []}\n```"
    
    state = {
        "start_date": "2024-05-01",
        "end_date": "2024-05-05",
        "destination": {"city": "Tokyo"},
        "budget": 5000,
        "preferences": [],
        "travel_type": "standard",
        "flights": [],
        "hotels": [],
        "activities": [],
        "restaurants": []
    }
    
    result = await itinerary_builder_node(state)
    
    assert "itinerary_raw" in result
    assert result["status"] == "optimizing_plan"
