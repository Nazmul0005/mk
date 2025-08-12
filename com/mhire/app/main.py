from fastapi import FastAPI
from com.mhire.app.services.preferences.preferences_router import router as preferences_router
from com.mhire.app.services.notification.notification_router import router as notification_router
from com.mhire.app.services.date_mate.date_mate_router import router as date_mate_router

# Create FastAPI application
app = FastAPI(
    title="AI-Powered Dating Analysis API",
    description="Analyze user conversations and profiles using OpenAI to extract UserPreference format",
    version="1.0.0"
)

# Include routers
app.include_router(preferences_router)
app.include_router(notification_router)
app.include_router(date_mate_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI-Powered UserPreference Analysis API",
        "description": "Analyze user conversations to extract UserPreference format using OpenAI",
        "version": "1.0.0",
        "main_endpoints": {
            "user_preference_analysis": "/api/v1/chats/analyze/{user_id} (POST)",
            "get_conversations": "/api/v1/chats/ai-conversation/{user_id} (GET)",
            "get_messages_only": "/api/v1/chats/messages/{user_id} (GET)",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "example_usage": {
            "analyze_user": "POST /api/v1/chats/analyze/682afd59c3a390babf9a9bb4",
            "description": "Analyzes last 100 conversations and returns UserPreference format"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "preferences-analysis-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)