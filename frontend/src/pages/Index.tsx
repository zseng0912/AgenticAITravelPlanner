import { useState, useCallback } from "react";
import Header from "@/components/travel/Header";
import TravelForm from "@/components/travel/TravelForm";
import PlanningProgress from "@/components/travel/PlanningProgress";
import ItineraryDisplay from "@/components/travel/ItineraryDisplay";

type Phase = "form" | "planning" | "results";

/**
 * Main Index Page Component
 * Manages the top-level state of the travel planning application.
 * Switches between three main phases: 'form', 'planning', and 'results'.
 */
const Index = () => {
  // Application phases:
  // - 'form': User inputs their trip preferences
  // - 'planning': Backend agents are researching and generating the plan
  // - 'results': Final itinerary is displayed to the user
  const [phase, setPhase] = useState<Phase>("form");
  
  // Real-time status updates from the backend (Server-Sent Events)
  const [status, setStatus] = useState("understanding_request");
  
  // The final structured itinerary object
  const [itinerary, setItinerary] = useState<any>(null);
  
  // Store form data to allow regeneration without re-typing
  const [formData, setFormData] = useState<any>(null);

  /**
   * Handlers the form submission and initiates the SSE stream with the backend.
   */
  const handleGenerate = async (data: any) => {
    setFormData(data);
    setPhase("planning");
    setStatus("understanding_request");

    try {
      // Connect to the streaming endpoint
      const response = await fetch("http://localhost:8000/api/generate-itinerary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.body) return;

      // Handle the streaming response from FastAPI
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          // Parse SSE data chunks (prefixed with 'data: ')
          if (line.startsWith("data: ")) {
            try {
              const payload = JSON.parse(line.substring(6));
              
              // Update progress status based on backend node execution
              if (payload.status) {
                setStatus(payload.status);
              }
              
              // If the final itinerary is received, switch to results view
              if (payload.itinerary) {
                setItinerary(payload.itinerary);
                if (payload.status === "completed") {
                  setPhase("results");
                }
              }
            } catch (e) {
              console.error("Error parsing stream chunk:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error generating itinerary:", error);
      alert("Failed to generate itinerary. Please check if the backend is running at http://localhost:8000");
      setPhase("form");
    }
  };

  const handleRegenerate = () => {
    if (formData) {
      handleGenerate(formData);
    } else {
      setPhase("form");
    }
  };

  const handleEditPreferences = () => setPhase("form");

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-2xl mx-auto px-4 pb-16">
        <Header />

        {phase === "form" && <TravelForm onGenerate={handleGenerate} initialData={formData} />}

        {phase === "planning" && (
          <PlanningProgress status={status} />
        )}

        {phase === "results" && (
          <ItineraryDisplay
            itinerary={itinerary}
            onRegenerate={handleRegenerate}
            onEditPreferences={handleEditPreferences}
          />
        )}
      </div>
    </div>
  );
};

export default Index;
