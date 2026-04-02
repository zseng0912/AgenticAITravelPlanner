import pytest
import json
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch, MagicMock

client = TestClient(app)

@pytest.fixture
def mock_workflow():
    with patch("app.routes.travel.app_workflow.astream") as mock_astream:
        yield mock_astream

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_generate_itinerary_api(mock_workflow):
    # Setup mock astream to yield some progress and then a final state
    mock_workflow.return_value = AsyncMock()
    
    # Simulate astream yielding values
    async def mock_astream_generator(*args, **kwargs):
        yield {"planner": {"status": "searching_flights"}}
        yield {"flights": {"status": "searching_hotels"}}
        yield {"optimizer": {"itinerary_final": {"days": []}, "status": "completed"}}
        
    mock_workflow.side_effect = mock_astream_generator
    
    payload = {
        "intent": "Trip to Tokyo",
        "destination": "Tokyo",
        "start_date": "2024-05-01",
        "end_date": "2024-05-05",
        "budget": 5000,
        "travel_type": "standard",
        "num_people": 2,
        "preferences": ["sushi"]
    }
    
    # The endpoint is an EventSource (StreamingResponse)
    with client.stream("POST", "/api/generate-itinerary", json=payload) as response:
        assert response.status_code == 200
        
        # Collect and parse data chunks
        events = []
        for line in response.iter_lines():
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)
        
        assert any(e.get("status") == "searching_flights" for e in events)
        assert any(e.get("status") == "completed" for e in events)
        assert any("itinerary" in e for e in events)

def test_search_airports_api():
    with patch("app.services.serpapi_service.serpapi_service.search_airports_dynamic", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{"iata": "NRT", "name": "Narita"}]
        
        response = client.get("/api/airports/search?q=Tokyo")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["iata"] == "NRT"
