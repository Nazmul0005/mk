from fastapi import APIRouter, HTTPException
from datetime import datetime
import httpx
from com.mhire.app.services.preferences.preferences import PreferencesService
from com.mhire.app.services.preferences.preferences_schema import (
    UserPreferenceResponse, 
    ConversationResponse, 
    DataAnalyzed,
    ErrorResponse,
    UserPreference
)

# Create router instance
router = APIRouter(prefix="/api/v1/chats", tags=["User Preferences"])

@router.get("/ai-conversation/{user_id}", response_model=dict)
async def get_user_conversations(user_id: str):
    """
    Get all conversations for a specific user using their user_id from URL path
    This matches your existing API structure
    """
    try:
        result = await PreferencesService.fetch_user_conversations(user_id)
        return result
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/messages/{user_id}", response_model=ConversationResponse)
async def get_user_messages_only(user_id: str):
    """
    Get only the conversation messages without user info
    """
    try:
        result = await PreferencesService.fetch_user_messages_only(user_id)
        
        if result.get("success"):
            return ConversationResponse(
                success=True,
                user_id=user_id,
                messages=result["messages"],
                total_messages=result["total_messages"]
            )
        else:
            raise HTTPException(status_code=404, detail="User conversations not found")
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/analyze/{user_id}", response_model=UserPreference)
async def analyze_user_conversations(user_id: str):
    """
    POST method that:
    1. Takes user_id from URL path
    2. Automatically fetches all user data from the existing endpoint
    3. Analyzes last 100 conversations using OpenAI
    4. Returns UserPreference format response
    """
    try:
        # Step 1: Automatically fetch user data using the user_id
        user_data = await PreferencesService.fetch_user_conversations(user_id)
        
        if not user_data.get("success"):
            raise HTTPException(status_code=404, detail="User data not found")
        
        # Step 2: Prepare data for AI analysis
        analysis_data = PreferencesService.prepare_analysis_data(user_id, user_data)
        
        # Step 3: Analyze conversations using OpenAI
        user_preferences = await PreferencesService.analyze_conversations_for_user_preferences(analysis_data)
        
        # Return user preferences directly
        return user_preferences
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user data: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")