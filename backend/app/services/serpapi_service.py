import os
import aiohttp
from typing import Dict, Any, List
from app.config import settings
from urllib.parse import quote

class SerpAPIService:
    """
    Service to interact with SerpApi for real-time travel data.
    Provides methods for searching flights, hotels, restaurants, and activities.
    """
    def __init__(self):
        self.api_key = settings.SERPAPI_API_KEY
        self.base_url = "https://serpapi.com/search"

    async def _fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper method to perform asynchronous GET requests to SerpApi.
        """
        params["api_key"] = self.api_key
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"SerpAPI error: {response.status}"}

    async def search_flights(self, departure: str, arrival: str, outbound_date: str, return_date: str) -> List[Dict[str, Any]]:
        """
        Searches for round-trip flights using the Google Flights engine.
        Returns a list of flight options with pricing and leg details.
        """
        if not self.api_key or "your_serpapi_key_here" in self.api_key:
            print(f"SerpAPI key not set, using mock data for flights from {departure} to {arrival}")
            mock_flights = [
                {
                    "airline": "Japan Airlines", 
                    "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/JL.png",
                    "price": "RM 1,200", 
                    "departure": "10:00 AM", 
                    "arrival": "10:00 PM", 
                    "origin": departure,
                    "destination": arrival,
                    "duration": "12h 0m",
                    "stops": "1 stop(s)",
                    "booking_link": "https://www.jal.co.jp/",
                    "legs": [
                        {
                            "airline": "Japan Airlines",
                            "flight_number": "JL123",
                            "departure_airport": f"{departure} International",
                            "departure_iata": departure,
                            "departure_time": "10:00 AM",
                            "arrival_airport": "Tokyo Narita",
                            "arrival_iata": "NRT",
                            "arrival_time": "2:00 PM",
                            "duration": "4h 0m"
                        },
                        {
                            "airline": "Japan Airlines",
                            "flight_number": "JL456",
                            "departure_airport": "Tokyo Narita",
                            "departure_iata": "NRT",
                            "departure_time": "6:00 PM",
                            "arrival_airport": f"{arrival} International",
                            "arrival_iata": arrival,
                            "arrival_time": "10:00 PM",
                            "duration": "4h 0m"
                        }
                    ]
                }
            ]
            return mock_flights

        params = {
            "engine": "google_flights",
            "departure_id": departure,
            "arrival_id": arrival,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "currency": "MYR",
            "hl": "en"
        }
        query = f"Flights from {departure} to {arrival} on {outbound_date} through {return_date}"

        result = await self._fetch(params)
        flights = []
        if "best_flights" in result:
            for flight in result["best_flights"][:3]:
                legs = []
                for f in flight.get("flights", []):
                    legs.append({
                        "airline": f.get("airline"),
                        "airline_logo": f.get("airline_logo"),
                        "flight_number": f.get("flight_number"),
                        "departure_airport": f.get("departure_airport", {}).get("name"),
                        "departure_iata": f.get("departure_airport", {}).get("id"),
                        "departure_time": f.get("departure_airport", {}).get("time"),
                        "arrival_airport": f.get("arrival_airport", {}).get("name"),
                        "arrival_iata": f.get("arrival_airport", {}).get("id"),
                        "arrival_time": f.get("arrival_airport", {}).get("time"),
                        "duration": f"{f.get('duration', 0) // 60}h {f.get('duration', 0) % 60}m"
                    })
                
                first_leg = legs[0] if legs else {}
                last_leg = legs[-1] if legs else {}
                
                flights.append({
                    "airline": first_leg.get("airline"),
                    "airline_logo": first_leg.get("airline_logo"),
                    "price": flight.get("price"),
                    "departure": first_leg.get("departure_time"),
                    "arrival": last_leg.get("arrival_time"),
                    "origin": first_leg.get("departure_iata"),
                    "destination": last_leg.get("arrival_iata"),
                    "duration": f"{flight.get('total_duration', 0) // 60}h {flight.get('total_duration', 0) % 60}m",
                    "stops": "Nonstop" if len(legs) == 1 else f"{len(legs) - 1} stop(s)",
                    "legs": legs,
                    "booking_link": f"https://www.google.com/travel/flights?q={quote(query)}&hl=en&currency=MYR"
                })
        return flights

    async def search_hotels(self, location: str, check_in: str, check_out: str, min_price: int = 0, max_price: int = 0, adults: int = 1) -> List[Dict[str, Any]]:
        """
        Searches for hotels in a specific location using the Google Hotels engine.
        Filters by date range, budget, and number of guests.
        """
        if not self.api_key or "your_serpapi_key_here" in self.api_key:
            print(f"SerpAPI key not set, using mock data for hotels in {location} (Price: {min_price}-{max_price}, Adults: {adults})")
            return [
                {
                    "name": "Park Hyatt Tokyo", 
                    "price": "RM 1,500", 
                    "rating": 4.8, 
                    "maps_link": "https://maps.google.com", 
                    "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80",
                    "booking_link": "https://www.hyatt.com/en-US/hotel/japan/park-hyatt-tokyo/tyoph",
                    "description": "Luxurious stay with iconic city views."
                },
                {
                    "name": "The Ritz-Carlton, Tokyo", 
                    "price": "RM 1,800", 
                    "rating": 4.9, 
                    "maps_link": "https://maps.google.com", 
                    "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
                    "booking_link": "https://www.ritzcarlton.com/en/hotels/japan/tokyo",
                    "description": "Elegant rooms in the heart of Roppongi."
                }
            ]
        params = {
            "engine": "google_hotels",
            "q": location,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "currency": "MYR",
            "adults": adults,
            "hl": "en"
        }
        
        if min_price > 0:
            params["min_price"] = min_price
        if max_price > 0:
            params["max_price"] = max_price

        result = await self._fetch(params)
        hotels = []
        if "properties" in result:
            for hotel in result["properties"][:3]:
                hotels.append({
                    "name": hotel.get("name"),
                    "price": f"RM {hotel.get('rate_per_night', {}).get('lowest')}",
                    "rating": hotel.get("overall_rating"),
                    "maps_link": f"https://www.google.com/maps/search/{quote(hotel.get('name'))}",
                    "image": hotel.get("images", [{}])[0].get("thumbnail"),
                    "booking_link": hotel.get("link"), # Specific booking link from SerpAPI
                    "description": hotel.get("description", "Excellent choice for your stay.")
                })
        print(location)
        return hotels

    async def search_airports_dynamic(self, query: str) -> List[Dict[str, str]]:
        if not self.api_key or "your_serpapi_key_here" in self.api_key:
            from app.services.airport_service import search_airports
            return search_airports(query)

        params = {
            "engine": "google_flights_autocomplete",
            "q": query,
            "hl": "en",
            "gl": "us"
        }
        result = await self._fetch(params)
        normalized_results = []
        
        if "suggestions" in result:
            for suggestion in result["suggestions"]:
                # Handle direct airport matches
                if suggestion.get("type") == "airport":
                    normalized_results.append({
                        "iata": suggestion.get("id"),
                        "name": suggestion.get("name"),
                        "city": suggestion.get("description", "").split(",")[0],
                        "country": suggestion.get("description", "").split(",")[-1].strip()
                    })
                # Handle city matches by adding the city as a selectable option (Google Flights accepts city IDs)
                elif suggestion.get("type") == "city":
                    normalized_results.append({
                        "iata": suggestion.get("id"),
                        "name": f"All Airports in {suggestion.get('name')}",
                        "city": suggestion.get("name").split(",")[0],
                        "country": suggestion.get("name").split(",")[-1].strip()
                    })
                    # Also add specific airports if available in the suggestion
                    for airport in suggestion.get("airports", []):
                        normalized_results.append({
                            "iata": airport.get("id"),
                            "name": airport.get("name"),
                            "city": airport.get("city"),
                            "country": suggestion.get("name").split(",")[-1].strip()
                        })
        
        # Deduplicate by IATA
        seen = set()
        unique_results = []
        for res in normalized_results:
            if res["iata"] not in seen:
                seen.add(res["iata"])
                unique_results.append(res)
                
        return unique_results[:20]

    async def search_restaurants(self, location: str, preferences: List[str]) -> List[Dict[str, Any]]:
        """
        Searches for restaurants based on location and culinary preferences.
        Uses the TripAdvisor engine via SerpApi.
        """
        if not self.api_key or "your_serpapi_key_here" in self.api_key:
            print("SerpAPI key not set, using mock data for restaurants")
            return [
                {"name": "Ichiran Ramen", "description": "Famous ramen chain", "price": "RM 50-80", "rating": 4.5, "maps_link": "https://maps.google.com", "photo_url": "https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=600&q=80"},
                {"name": "Sushi Saito", "description": "High-end sushi experience", "price": "RM 500-1000", "rating": 4.8, "maps_link": "https://maps.google.com", "photo_url": "https://images.unsplash.com/photo-1580822222538-0d4c49b54c05?w=600&q=80"}
            ]
        
        query = f"best restaurants in {location} {' '.join(preferences)}"
        params = {
            "engine": "tripadvisor",
            "q": query,
            "ssrc": "r"  # Restaurant-specific search
        }
        
        result = await self._fetch(params)
        restaurants = []
        
        if "places" in result:
            for place in result["places"][:20]:  # Get top 10 results
                restaurants.append({
                    "name": place.get("title"),
                    "description": place.get("description", "Restaurant"),
                    "price": "Varies",
                    "rating": place.get("rating"),
                    "maps_link": place.get("link"),
                    "photo_url": place.get("thumbnail")
                })
        return restaurants

    async def search_activities(self, location: str, preferences: List[str]) -> List[Dict[str, Any]]:
        """
        Searches for things to do and local attractions.
        Uses TripAdvisor or Google Local engines.
        """
        if not self.api_key or "your_serpapi_key_here" in self.api_key:
            print("SerpAPI key not set, using mock data for activities")
            return [
                {"name": "Shibuya Crossing", "description": "Famous crossing", "price": "Free", "maps_link": "https://maps.google.com", "photo_url": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=600&q=80"},
                {"name": "Meiji Jingu Shrine", "description": "Beautiful shrine in a forest", "price": "Free", "maps_link": "https://maps.google.com", "photo_url": "https://images.unsplash.com/photo-1583766395091-2eb9f4040d20?w=600&q=80"}
            ]
        
        query = f"best things to do in {location} {' '.join(preferences)}"
        params = {
            "engine": "tripadvisor",
            "q": query,
            "ssrc": "A"  # Attraction-specific search
        }
        
        result = await self._fetch(params)
        activities = []
        
        if "places" in result:
            for place in result["places"][:20]:  # Get top 10 results
                activities.append({
                    "name": place.get("title"),
                    "description": place.get("description", "Activity"),
                    "price": "Varies",
                    "rating": place.get("rating"),
                    "maps_link": place.get("link"),
                    "photo_url": place.get("thumbnail")
                })
        return activities

serpapi_service = SerpAPIService()
