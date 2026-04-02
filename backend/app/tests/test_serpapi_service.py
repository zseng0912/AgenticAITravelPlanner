import pytest
from unittest.mock import AsyncMock, patch
from app.services.serpapi_service import SerpAPIService

@pytest.fixture
def serpapi_service():
    return SerpAPIService()

@pytest.mark.asyncio
async def test_search_flights_mock_mode(serpapi_service):
    # Force mock mode by setting api_key to something that triggers it
    serpapi_service.api_key = "your_serpapi_key_here"
    
    flights = await serpapi_service.search_flights("LAX", "NRT", "2024-05-01", "2024-05-10")
    
    assert isinstance(flights, list)
    assert len(flights) > 0
    assert flights[0]["airline"] == "Japan Airlines"
    assert flights[0]["origin"] == "LAX"
    assert flights[0]["destination"] == "NRT"

@pytest.mark.asyncio
async def test_search_hotels_mock_mode(serpapi_service):
    serpapi_service.api_key = "your_serpapi_key_here"
    
    hotels = await serpapi_service.search_hotels("Tokyo", "2024-05-01", "2024-05-10")
    
    assert isinstance(hotels, list)
    assert len(hotels) > 0
    assert hotels[0]["name"] == "Park Hyatt Tokyo"

@pytest.mark.asyncio
async def test_search_restaurants_mock_mode(serpapi_service):
    serpapi_service.api_key = "your_serpapi_key_here"
    
    restaurants = await serpapi_service.search_restaurants("Tokyo", ["sushi"])
    
    assert isinstance(restaurants, list)
    assert len(restaurants) > 0
    assert "Ichiran" in restaurants[0]["name"] or "Sushi Saito" in restaurants[0]["name"] or "Sushi Saito" in restaurants[1]["name"]

@pytest.mark.asyncio
async def test_search_activities_mock_mode(serpapi_service):
    serpapi_service.api_key = "your_serpapi_key_here"
    
    activities = await serpapi_service.search_activities("Tokyo", ["culture"])
    
    assert isinstance(activities, list)
    assert len(activities) > 0
    assert "Shibuya" in activities[0]["name"] or "Meiji" in activities[1]["name"]

@pytest.mark.asyncio
@patch("app.services.serpapi_service.SerpAPIService._fetch", new_callable=AsyncMock)
async def test_search_flights_live_logic(mock_fetch, serpapi_service):
    # Set a real-looking key to avoid mock mode
    serpapi_service.api_key = "real_key_123"
    
    # Mock return value for _fetch
    mock_fetch.return_value = {
        "best_flights": [
            {
                "flights": [
                    {
                        "airline": "ANA",
                        "airline_logo": "logo.png",
                        "flight_number": "NH1",
                        "departure_airport": {"name": "LAX", "id": "LAX", "time": "10:00 AM"},
                        "arrival_airport": {"name": "NRT", "id": "NRT", "time": "2:00 PM"},
                        "duration": 600
                    }
                ],
                "price": 1000,
                "total_duration": 600
            }
        ]
    }
    
    flights = await serpapi_service.search_flights("LAX", "NRT", "2024-05-01", "2024-05-10")
    
    assert len(flights) == 1
    assert flights[0]["airline"] == "ANA"
    assert flights[0]["price"] == 1000
    mock_fetch.assert_called_once()

@pytest.mark.asyncio
@patch("app.services.serpapi_service.SerpAPIService._fetch", new_callable=AsyncMock)
async def test_search_restaurants_live_logic(mock_fetch, serpapi_service):
    serpapi_service.api_key = "real_key_123"
    
    mock_fetch.return_value = {
        "places": [
            {
                "title": "Local Sushi",
                "description": "Great sushi",
                "rating": 4.5,
                "link": "https://tripadvisor.com/123",
                "thumbnail": "thumb.jpg"
            }
        ]
    }
    
    restaurants = await serpapi_service.search_restaurants("Tokyo", ["sushi"])
    
    assert len(restaurants) == 1
    assert restaurants[0]["name"] == "Local Sushi"
    assert restaurants[0]["rating"] == 4.5
    assert mock_fetch.call_args[0][0]["ssrc"] == "r"
