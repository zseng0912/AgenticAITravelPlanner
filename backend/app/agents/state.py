from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    Defines the shared state maintained throughout the LangGraph workflow.
    This object is passed between nodes and updated incrementally.
    """
    # User-provided Input Data
    intent: str           # The raw natural language request from the user
    departure: str        # Departure city/airport code
    destination: str      # Destination city or structured destination info
    start_date: str       # Trip start date (YYYY-MM-DD)
    end_date: str         # Trip end date (YYYY-MM-DD)
    budget: float         # Total budget for the trip
    preferences: List[str] # List of user travel preferences (e.g., "sushi", "museums")
    travel_type: str      # Category of travel (e.g., "standard", "luxury", "budget")
    num_people: int       # Number of travelers
    
    # Internal Processing Data (Populated by nodes)
    tasks: List[str]                  # List of sub-tasks identified by the planner
    budget_decomposition: Dict[str, Any] # Breakdown of budget into flights, hotels, etc.
    hotel_min_price: int             # Calculated minimum hotel price per night
    hotel_max_price: int             # Calculated maximum hotel price per night
    flights: List[Dict[str, Any]]     # List of flight options found
    return_flights: List[Dict[str, Any]] # List of return flight options (if separate)
    hotels: List[Dict[str, Any]]      # List of hotel options found
    activities: List[Dict[str, Any]]  # List of recommended activities
    restaurants: List[Dict[str, Any]] # List of recommended restaurants
    itinerary_raw: str                # Raw text/markdown output from the LLM
    itinerary_final: Dict[str, Any]   # Structured JSON representation of the final plan
    
    # Execution Status
    status: str                       # Current progress indicator (e.g., "searching_flights")
