from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.travel import router as travel_router
from app.config import settings

app = FastAPI(title="Agentic AI Travel Planner Backend")

# Enable CORS to allow the frontend (Vite/React) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register travel planning routes under the /api prefix
app.include_router(travel_router, prefix="/api")

@app.get("/api/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.get("/")
def root():
    """Root endpoint providing basic API info."""
    return {
        "message": "Agentic AI Travel Planner API is running 🚀",
        "status": "ready"
    }

if __name__ == "__main__":
    # Start the FastAPI server using Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
