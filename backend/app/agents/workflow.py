from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import (
    planner_node,
    flight_search_node,
    hotel_search_node,
    activities_node,
    itinerary_builder_node,
    optimization_node
)

def create_workflow() -> StateGraph:
    """
    Orchestrates the multi-agent workflow using LangGraph.
    Defines the nodes and the execution sequence (linear pipeline).
    """
    # Initialize the graph with the defined state schema
    workflow = StateGraph(AgentState)

    # Add processing nodes to the graph
    workflow.add_node("planner", planner_node)
    workflow.add_node("flights", flight_search_node)
    workflow.add_node("hotels", hotel_search_node)
    workflow.add_node("activities", activities_node)
    workflow.add_node("itinerary", itinerary_builder_node)
    workflow.add_node("optimizer", optimization_node)

    # Define the execution edges (Linear pipeline sequence)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "flights")
    workflow.add_edge("flights", "hotels")
    workflow.add_edge("hotels", "activities")
    workflow.add_edge("activities", "itinerary")
    workflow.add_edge("itinerary", "optimizer")
    workflow.add_edge("optimizer", END)

    return workflow

# Compile the graph into an executable application
app_workflow = create_workflow().compile()
