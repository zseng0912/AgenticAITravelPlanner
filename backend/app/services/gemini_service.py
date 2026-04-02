from typing import List, Dict, Any
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings

class GeminiService:
    """
    Service to interact with Google Gemini LLM for travel planning logic.
    Handles request analysis, budget decomposition, and final itinerary generation.
    """
    def __init__(self):
        # Initialize the LangChain ChatGoogleGenerativeAI wrapper
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7
        )

    async def analyze_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes a natural language travel request to extract structured parameters.
        Returns a JSON object with normalized destination, budget breakdown, and trip metadata.
        """
        try:
            prompt = f"""
    You are a travel planning AI (Planner Node in an agentic system).

    Your job:
    1. Normalize destination into:
    - IATA airport code
    - city
    - country
    2. Decompose budget into realistic ranges
    3. Ensure all outputs are structured and usable by downstream systems

    User Input:
    Intent: {data.get('intent')}
    Destination: {data.get('destination')}
    Duration: {data.get('days')} days
    Total Budget: RM {data.get('budget')}
    Travel Type: {data.get('travel_type')}
    Number of People: {data.get('num_people')}

    Rules:
    - Flights use IATA codes (e.g., SIN, NRT)
    - Hotels use city + country (e.g., Singapore, Singapore)
    - Budget must be ranges (min/max), NOT fixed values
    - Hotel per night = total hotel budget / duration
    - Keep allocations realistic

    Return ONLY valid JSON:

    {{
    "destination": {{
        "iata": "",
        "city": "",
        "country": ""
    }},
    "duration_days": 0,
    "num_people": 1,
    "budget": {{
        "total": 0,
        "flight": {{ "min": 0, "max": 0 }},
        "hotel": {{ "min": 0, "max": 0 }},
        "activities": {{ "min": 0, "max": 0 }}
    }},
    "hotel_per_night_range": [0, 0],
    "travel_type": "",
    "priority": "cost",
    "notes": ""
    }}
    """

            # Invoke the LLM with the structured prompt
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # ✅ Extract JSON content from potential Markdown code blocks
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)

            # ✅ Calculate per-night hotel budget based on duration
            days = max(result.get("duration_days", 1), 1)
            hotel_budget = result["budget"]["hotel"]

            result["hotel_per_night_range"] = [
                int(hotel_budget["min"] / days),
                int(hotel_budget["max"] / days)
            ]

            return result

        except Exception as e:
            print("Planner failed (Exception):", e)

            # ✅ Fallback logic if LLM analysis fails
            total = data.get('budget', 5000)
            days = data.get('days', 3)

            return {
                "destination": {
                    "iata": "",
                    "city": data.get("destination", ""),
                    "country": ""
                },
                "duration_days": days,
                "num_people": data.get("num_people", 1),
                "budget": {
                    "total": total,
                    "flight": {"min": int(total * 0.25), "max": int(total * 0.4)},
                    "hotel": {"min": int(total * 0.3), "max": int(total * 0.5)},
                    "activities": {"min": int(total * 0.1), "max": int(total * 0.2)}
                },
                "hotel_per_night_range": [int(total * 0.1), int(total * 0.2)],
                "travel_type": data.get("travel_type", "standard"),
                "priority": "cost",
                "notes": "Fallback allocation used."
            }

    async def generate_itinerary(self, data: Dict[str, Any]) -> str:
        """
        Synthesizes all researched data (flights, hotels, activities) into a 
        complete day-by-day JSON itinerary.
        """
        # Mock response for development if API key is missing
        if not settings.GEMINI_API_KEY or "your_gemini_key_here" in settings.GEMINI_API_KEY:
            print("Gemini API key not set, using mock response")
            mock_response = {
                "hotel": {
                    "name": "Park Hyatt Tokyo",
                    "price": "RM 1,500 per night",
                    "rating": 4.8,
                    "description": "Luxurious stay with iconic city views, as featured in 'Lost in Translation'.",
                    "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80",
                    "booking_url": "https://www.hyatt.com/en-US/hotel/japan/park-hyatt-tokyo/tyoph",
                    "maps_url": "https://maps.google.com/?q=Park+Hyatt+Tokyo"
                },
                "days": [
                    {
                        "day": 1,
                        "title": f"Welcome to {data.get('destination')}",
                        "activities": [
                            {
                                "time": "10:00 AM",
                                "location": "City Center",
                                "desc": "Exploring the heart of the city",
                                "details": f"A wonderful start to your trip in {data.get('destination')}. Enjoy the local culture and landmarks.",
                                "price": "Free",
                                "image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&q=80",
                                "mapsLink": "https://maps.google.com",
                                "bookingUrl": "",
                                "bookingLabel": ""
                            }
                        ]
                    }
                ],
                "budget_summary": [
                    {"category": "✈️ Flights", "amount": 1200},
                    {"category": "🏨 Hotels", "amount": 1500},
                    {"category": "🍜 Food & Dining", "amount": 500}
                ],
                "total_budget": 3200
            }
            return f"```json\n{json.dumps(mock_response)}\n```"

        prompt = f"""
        Generate a day-by-day travel itinerary based on the following data:
        Destination: {data.get('destination')}
        Duration: {data.get('days')} days
        Budget: RM {data.get('budget')}
        Preferences: {data.get('preferences')}
        Travel Type: {data.get('travel_type')}
        Number of People: {data.get('num_people')}
        Budget Decomposition: {data.get('budget_decomposition')}

        Available Round-Trip Flights: {data.get('flights')}
        Available Hotels: {data.get('hotels')}
        Available Activities: {data.get('activities')}
        Available Restaurants: {data.get('restaurants')}

        Structure the output as a clean, structured JSON format. 
        
        CRITICAL RULES:
        1. Hotel Selection: You MUST select the best value hotel from the 'Available Hotels' list, considering its rating and price.
        2. Venue Selection: For the daily itinerary, you MUST select venues (restaurants and things to do) exclusively from the 'Available Activities' and 'Available Restaurants' lists. Choose a variety of options that have good ratings and fit the user's preferences.
        3. Daily Meals: Each day of the trip MUST include at least three meals (breakfast, lunch, and dinner), chosen from the 'Available Restaurants' list. The restaurant DO NOT repeat in the whole trip either same day or other days.
        4. Each day MUST include exactly:
            - 1 breakfast restaurant
            - 1 lunch restaurant
            - 1 dinner restaurant
        5. All 3 meals MUST be different restaurants.
        6. Activities MUST NOT repeat in the trip either same day or other days.
        7. Activities and meals MUST stay within the SAME AREA for that day.
        8. DO NOT move between distant areas within the same day.
        9. No Hallucination: DO NOT invent or create any venues, flights, or hotels. All selections MUST originate from the data provided in the 'Available' lists.
        10. Flight Information: The top-level "flights" key must contain "outbound" and "return" lists. Extract the legs from the provided round-trip flight options.

        RESPONSE JSON STRUCTURE:
        {{
            "hotel": {{
                "name": "Selected Hotel Name",
                "price": "Price per night in RM",
                "rating": "Rating (e.g. 4.5)",
                "description": "Short description of why this hotel was chosen",
                "image": "Hotel image URL",
                "booking_url": "USE THE booking_link PROVIDED IN THE AVAILABLE HOTELS DATA",
                "maps_url": "Google Maps link"
            }},
            "flights": {{
                "outbound": [
                    {{
                        "airline": "Airline Name",
                        "airline_logo": "Logo URL",
                        "price": "Price in RM",
                        "departure_date": "Departure Date like Sun, Apr 5",
                        "time": "Departure Time - Arrival Time",
                        "origin": "Origin IATA Code",
                        "destination": "Destination IATA Code",
                        "duration": "Total Flight Duration",
                        "stops": "Stops info",
                        "booking_url": "Booking URL",
                        "legs": [
                            {{
                                "airline": "Leg Airline",
                                "flight_number": "Flight Number",
                                "departure_airport": "Departure Airport Name",
                                "departure_iata": "IATA",
                                "departure_time": "Time",
                                "arrival_airport": "Arrival Airport Name",
                                "image_url": "Google Photos URL of Arrival Airport Name",
                                "arrival_iata": "IATA",
                                "arrival_time": "Time",
                                "duration": "Leg Duration"
                            }}
                        ]
                    }}
                ]
            }},
            "days": [
                {{
                    "day": 1,
                    "title": "Day 1 Title",
                    "activities": [
                        {{
                            "time": "e.g. 09:00 AM",
                            "location": "Location Name from provided data",
                            "desc": "Short catchy description of the activity or meal",
                            "details": "More detailed information about the activity/restaurant",
                            "price": "Price in RM or 'Varies'",
                            "image": "USE THE 'photo_url'or 'image' FROM THE PROVIDED DATA. DO NOT USE GENERIC IMAGES.",
                            "mapsLink": "'maps_link' or 'link' from the provided data",
                            "bookingUrl": "Booking URL if applicable",
                            "bookingLabel": "Label for booking button (e.g. 'Book Tickets')"
                        }}
                    ]
                }}
            ],
            "budget_summary": [
                {{"category": "✈️ Flights", "amount": 1200}},
                {{"category": "🏨 Hotels", "amount": 2000}},
                {{"category": "🍜 Food & Dining", "amount": 800}},
                {{"category": "🎫 Activities", "amount": 500}},
                {{"category": "🚃 Transport", "amount": 200}}
            ],
            "total_budget": 4700
        }}

        Ensure the total budget is respected and all prices are in RM.
        """
        
        # Invoke LLM to build the final plan
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content

gemini_service = GeminiService()
