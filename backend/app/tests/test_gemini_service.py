import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.gemini_service import GeminiService

@pytest.fixture
def gemini_service():
    with patch("app.services.gemini_service.ChatGoogleGenerativeAI"):
        return GeminiService()

@pytest.mark.asyncio
async def test_analyze_request_fallback(gemini_service):
    # Mock llm to raise exception to trigger fallback
    gemini_service.llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))
    
    data = {
        "intent": "Plan a trip to Tokyo",
        "destination": "Tokyo",
        "days": 5,
        "budget": 5000,
        "travel_type": "standard",
        "num_people": 2
    }
    
    result = await gemini_service.analyze_request(data)
    
    assert result["destination"]["city"] == "Tokyo"
    assert result["budget"]["total"] == 5000
    assert "Fallback allocation used." in result["notes"]

@pytest.mark.asyncio
async def test_analyze_request_success(gemini_service):
    # Mock successful JSON response
    mock_json = {
        "destination": {"iata": "NRT", "city": "Tokyo", "country": "Japan"},
        "duration_days": 5,
        "num_people": 2,
        "budget": {
            "total": 5000,
            "flight": {"min": 1000, "max": 1500},
            "hotel": {"min": 2000, "max": 2500},
            "activities": {"min": 500, "max": 1000}
        },
        "hotel_per_night_range": [400, 500],
        "travel_type": "luxury",
        "priority": "experience",
        "notes": "Custom plan"
    }
    
    mock_response = MagicMock()
    mock_response.content = f"```json\n{json.dumps(mock_json)}\n```"
    gemini_service.llm.ainvoke = AsyncMock(return_value=mock_response)
    
    data = {
        "intent": "Plan a trip to Tokyo",
        "destination": "Tokyo",
        "days": 5,
        "budget": 5000,
        "travel_type": "luxury",
        "num_people": 2
    }
    
    result = await gemini_service.analyze_request(data)
    
    assert result["destination"]["iata"] == "NRT"
    assert result["hotel_per_night_range"] == [400, 500]
    assert result["travel_type"] == "luxury"

@pytest.mark.asyncio
async def test_generate_itinerary_mock_mode(gemini_service):
    # Set a mock key
    with patch("app.services.gemini_service.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "your_gemini_key_here"
        
        data = {"destination": "Tokyo", "days": 3}
        itinerary_str = await gemini_service.generate_itinerary(data)
        
        # Should return a string containing markdown json
        assert "```json" in itinerary_str
        assert "Park Hyatt Tokyo" in itinerary_str
