from fastapi import FastAPI

app = FastAPI(
    title="StayPilot AI",
    description="Multi-Agentic Voice AI Hotel Concierge",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "application": "StayPilot AI",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
