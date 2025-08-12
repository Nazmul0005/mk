from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

# Enum types for UserPreference
GenderType = Literal["MALE", "FEMALE", "OTHER"]
PreferenceLevelType = Literal["YES", "NO", "MAYBE"]
RelationshipGoalType = Literal["CASUAL", "LONG_TERM", "MARRIAGE", "FRIENDSHIP"]
ReligionType = Literal["ISLAM", "HINDUISM", "CHRISTIANITY", "BUDDHISM", "ATHEIST", "AGNOSTIC", "OTHER"]
EducationLevelType = Literal["HIGH_SCHOOL", "BACHELORS", "MASTERS", "DOCTORATE", "DIPLOMA", "OTHER"]
PersonalityType = Literal["INTROVERT", "EXTROVERT", "AMBIVERT", "ANALYTICAL", "EMOTIONAL", "ADVENTUROUS", "CALM", "FUNNY", "SERIOUS"]
LifestyleOptionType = Literal["FITNESS", "TRAVEL", "NIGHTLIFE", "FAMILY_ORIENTED", "VEGAN", "PET_LOVER", "TECH_SAVVY", "NATURE_LOVER"]
PoliticalViewType = Literal["LIBERAL", "CONSERVATIVE", "MODERATE", "APOLITICAL", "OTHER"]
LoveLanguageType = Literal["WORDS_OF_AFFIRMATION", "ACTS_OF_SERVICE", "RECEIVING_GIFTS", "QUALITY_TIME", "PHYSICAL_TOUCH"]
LanguageType = Literal["ENGLISH", "BENGALI", "HINDI", "ARABIC", "FRENCH", "SPANISH", "MANDARIN", "OTHER"]

class UserPreference(BaseModel):
    """UserPreference API format model"""
    userId: str
    interestedIn: List[GenderType]
    ageRangeMin: int = Field(ge=18, description="Minimum age preference (≥18)")
    ageRangeMax: int = Field(ge=18, description="Maximum age preference (≥18)")
    personalityTypes: Optional[List[PersonalityType]] = None
    drinking: Optional[PreferenceLevelType] = None
    smoking: Optional[PreferenceLevelType] = None
    relationshipGoals: Optional[List[RelationshipGoalType]] = None
    religionPreference: Optional[List[ReligionType]] = None
    educationPreference: Optional[List[EducationLevelType]] = None
    lifestylePreferences: Optional[List[LifestyleOptionType]] = None
    hasChildren: Optional[PreferenceLevelType] = None
    wantsChildren: Optional[PreferenceLevelType] = None
    openToLongDistance: Optional[bool] = None
    politicalView: Optional[PoliticalViewType] = None
    loveLanguage: Optional[List[LoveLanguageType]] = None
    preferredLanguages: Optional[List[LanguageType]] = None
    incomeMin: Optional[int] = None
    incomeMax: Optional[int] = None

class ConversationMessage(BaseModel):
    """Individual conversation message model"""
    user_message: str
    ai_reply: str
    timestamp: str

class UserProfile(BaseModel):
    """User profile information model"""
    name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    relationship_status: Optional[str] = None
    profession: Optional[str] = None
    interested_in: Optional[str] = None
    preferences: Optional[dict] = None

class AnalysisData(BaseModel):
    """Data structure for analysis input"""
    user_id: str
    user_profile: UserProfile
    conversation_history: List[ConversationMessage]
    total_conversations: int

class DataAnalyzed(BaseModel):
    """Metadata about the analysis performed"""
    user_profile: bool
    conversation_count: int
    conversations_analyzed: int
    analysis_timestamp: str
    analysis_method: str

class UserPreferenceResponse(BaseModel):
    """Response model for user preference analysis"""
    user_preferences: UserPreference

class ConversationResponse(BaseModel):
    """Response model for conversation data"""
    success: bool
    user_id: str
    messages: List[dict]
    total_messages: int


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None