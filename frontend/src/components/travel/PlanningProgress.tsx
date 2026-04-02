import { useEffect, useState } from "react";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const STEPS = [
  { id: "understanding_request", label: "Understanding your request", icon: "🧠" },
  { id: "searching_flights", label: "Searching for flights", icon: "✈️" },
  { id: "searching_hotels", label: "Selecting accommodation", icon: "🏨" },
  { id: "searching_activities", label: "Searching activities", icon: "🎡" },
  { id: "building_itinerary", label: "Building itinerary", icon: "📋" },
  { id: "optimizing_plan", label: "Optimizing plan", icon: "⚡" },
  { id: "completed", label: "Finalizing results", icon: "✨" },
];

interface PlanningProgressProps {
  status: string;
}

const PlanningProgress = ({ status }: PlanningProgressProps) => {
  const getStatus = (stepId: string) => {
    const currentIndex = STEPS.findIndex((s) => s.id === status);
    const stepIndex = STEPS.findIndex((s) => s.id === stepId);

    if (currentIndex === -1) return "pending";
    if (stepIndex < currentIndex) return "done";
    if (stepIndex === currentIndex) return "active";
    return "pending";
  };

  return (
    <div className="bg-card rounded-2xl shadow-sm border border-border p-6 md:p-8 animate-fade-in">
      <h2 className="text-xl font-semibold mb-6 text-card-foreground">
        🤖 AI is planning your trip…
      </h2>
      <div className="space-y-4">
        {STEPS.map((step, i) => {
          const stepStatus = getStatus(step.id);
          return (
            <div
              key={step.id}
              className={cn(
                "flex items-center gap-4 p-3 rounded-xl transition-all duration-500",
                stepStatus === "active" && "bg-accent",
                stepStatus === "done" && "opacity-70"
              )}
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
                {stepStatus === "done" && (
                  <div className="w-8 h-8 rounded-full bg-success flex items-center justify-center">
                    <Check className="h-4 w-4 text-success-foreground" />
                  </div>
                )}
                {stepStatus === "active" && (
                  <Loader2 className="h-6 w-6 text-primary animate-spin" />
                )}
                {stepStatus === "pending" && (
                  <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                    <span className="text-sm">{step.icon}</span>
                  </div>
                )}
              </div>
              <span
                className={cn(
                  "text-sm font-medium transition-colors",
                  stepStatus === "active" && "text-accent-foreground",
                  stepStatus === "done" && "text-muted-foreground",
                  stepStatus === "pending" && "text-muted-foreground"
                )}
              >
                {step.label}
              </span>
              {stepStatus === "active" && (
                <div className="ml-auto flex gap-1">
                  {[0, 1, 2].map((d) => (
                    <div
                      key={d}
                      className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse-dot"
                      style={{ animationDelay: `${d * 0.2}s` }}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PlanningProgress;
