from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class UserProfile(BaseModel):
    name: Optional[str] = ""
    age: Optional[str] = ""
    gender: Optional[str] = ""
    interested_in: List[str] = []
    relationship_goals: Optional[str] = ""
    hobbies: List[str] = []

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

class ChatState(BaseModel):
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    user_id: str