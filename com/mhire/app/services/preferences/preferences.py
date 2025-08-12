import httpx
import json
from datetime import datetime
from openai import OpenAI
from typing import Dict, List
from com.mhire.app.config.config import Config
from com.mhire.app.services.preferences.preferences_schema import UserPreference, AnalysisData, ConversationMessage, UserProfile

# Initialize configuration
config = Config()

# OpenAI client initialization
openai_client = OpenAI(api_key=config.openai_api_key) if config.openai_api_key else None

# External API base URL
EXISTING_API_BASE = "http://168.231.82.17:5000"

class PreferencesService:
    """Service class for handling user preference analysis"""
    
    @staticmethod
    async def fetch_user_conversations(user_id: str) -> dict:
        """
        Fetch user conversations from external API
        
        Args:
            user_id: User ID to fetch conversations for
            
        Returns:
            dict: API response with user data and conversations
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXISTING_API_BASE}/api/v1/chats/ai-conversation/{user_id}")
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def fetch_user_messages_only(user_id: str) -> dict:
        """
        Fetch only conversation messages for a user
        
        Args:
            user_id: User ID to fetch messages for
            
        Returns:
            dict: Simplified response with messages only
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXISTING_API_BASE}/api/v1/chats/ai-conversation/{user_id}")
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                return {
                    "success": True,
                    "user_id": user_id,
                    "messages": data["data"]["conversation"],
                    "total_messages": len(data["data"]["conversation"])
                }
            else:
                return {"success": False, "error": "User conversations not found"}
    
    @staticmethod
    def prepare_analysis_data(user_id: str, user_data: dict) -> AnalysisData:
        """
        Prepare user data for analysis
        
        Args:
            user_id: User ID
            user_data: Raw user data from API
            
        Returns:
            AnalysisData: Structured data for analysis
        """
        user_info = user_data["data"]["userInfo"]
        conversations = user_data["data"]["conversation"]
        
        user_profile = UserProfile(
            name=user_info.get("name"),
            age=user_info.get("dob"),
            gender=user_info.get("gender"),
            relationship_status=user_info.get("relationshipStatus"),
            profession=user_info.get("profession"),
            interested_in=user_info.get("interestedIn"),
            preferences=user_info.get("userPreference", {})
        )
        
        conversation_history = [
            ConversationMessage(
                user_message=conv["userMessage"]["content"],
                ai_reply=conv["aiReply"]["content"],
                timestamp=conv["userMessage"]["createdAt"]
            )
            for conv in conversations
        ]
        
        return AnalysisData(
            user_id=user_id,
            user_profile=user_profile,
            conversation_history=conversation_history,
            total_conversations=len(conversations)
        )
    
    @staticmethod
    async def analyze_conversations_for_user_preferences(data: AnalysisData) -> UserPreference:
        """
        Analyze user conversations using OpenAI to extract UserPreference format
        
        Args:
            data: Analysis data containing user profile and conversations
            
        Returns:
            UserPreference: Extracted user preferences
        """
        if not openai_client:
            # Fallback to basic preferences if OpenAI is not configured
            return UserPreference(
                userId=data.user_id,
                interestedIn=["FEMALE"],
                ageRangeMin=22,
                ageRangeMax=30,
                personalityTypes=["INTROVERT"],
                drinking="NO",
                smoking="NO",
                relationshipGoals=["LONG_TERM"],
                religionPreference=["OTHER"],
                educationPreference=["BACHELORS"],
                lifestylePreferences=["TECH_SAVVY"],
                hasChildren="NO",
                wantsChildren="MAYBE",
                openToLongDistance=True,
                politicalView="MODERATE",
                loveLanguage=["QUALITY_TIME"],
                preferredLanguages=["FRENCH"],
                incomeMin=30000,
                incomeMax=100000
            )
        
        try:
            # Prepare conversation text from last 100 conversations
            conversation_text = ""
            conversations_to_analyze = data.conversation_history[-100:]  # Last 100 conversations
            
            for i, conv in enumerate(conversations_to_analyze):
                conversation_text += f"\n--- Conversation {i+1} ---\n"
                conversation_text += f"Utilisateur: {conv.user_message}\n"
                conversation_text += f"Assistant IA: {conv.ai_reply}\n"
            
            # Create French-optimized UserPreference extraction prompt
            prompt = f"""
            Analysez l'historique de conversation suivant et extrayez les préférences utilisateur pour une plateforme de rencontres/matchmaking.
            La conversation est entre un UTILISATEUR et un assistant IA discutant des préférences de rencontres et des objectifs relationnels.
            
            IMPORTANT: Les conversations sont principalement en français. Comprenez les nuances culturelles françaises, l'argot, les expressions romantiques et les normes de rencontres françaises.

            PROFIL UTILISATEUR:
            - Nom: {data.user_profile.name}
            - Âge/Date de naissance: {data.user_profile.age}
            - Genre: {data.user_profile.gender}
            - Statut relationnel: {data.user_profile.relationship_status}
            - Profession: {data.user_profile.profession}
            - Intéressé par: {data.user_profile.interested_in}

            HISTORIQUE DE CONVERSATION ({len(conversations_to_analyze)} conversations analysées):
            {conversation_text}

            Basé sur cette conversation, extrayez et retournez un objet JSON avec la structure EXACTE suivante et les valeurs enum valides:

            {{
                "userId": "{data.user_id}",
                "interestedIn": ["MALE", "FEMALE", "OTHER"],
                "ageRangeMin": number,
                "ageRangeMax": number,
                "personalityTypes": ["INTROVERT", "EXTROVERT", "AMBIVERT", "ANALYTICAL", "EMOTIONAL", "ADVENTUROUS", "CALM", "FUNNY", "SERIOUS"],
                "drinking": "YES" | "NO" | "MAYBE",
                "smoking": "YES" | "NO" | "MAYBE",
                "relationshipGoals": ["CASUAL", "LONG_TERM", "MARRIAGE", "FRIENDSHIP"],
                "religionPreference": ["ISLAM", "HINDUISM", "CHRISTIANITY", "BUDDHISM", "ATHEIST", "AGNOSTIC", "OTHER"],
                "educationPreference": ["HIGH_SCHOOL", "BACHELORS", "MASTERS", "DOCTORATE", "DIPLOMA", "OTHER"],
                "lifestylePreferences": ["FITNESS", "TRAVEL", "NIGHTLIFE", "FAMILY_ORIENTED", "VEGAN", "PET_LOVER", "TECH_SAVVY", "NATURE_LOVER"],
                "hasChildren": "YES" | "NO" | "MAYBE",
                "wantsChildren": "YES" | "NO" | "MAYBE",
                "openToLongDistance": true | false,
                "politicalView": "LIBERAL" | "CONSERVATIVE" | "MODERATE" | "APOLITICAL" | "OTHER",
                "loveLanguage": ["WORDS_OF_AFFIRMATION", "ACTS_OF_SERVICE", "RECEIVING_GIFTS", "QUALITY_TIME", "PHYSICAL_TOUCH"],
                "preferredLanguages": ["ENGLISH", "BENGALI", "HINDI", "ARABIC", "FRENCH", "SPANISH", "MANDARIN", "OTHER"],
                "incomeMin": number,
                "incomeMax": number
            }}

            INSTRUCTIONS IMPORTANTES:
            1. Analysez attentivement les messages de l'UTILISATEUR pour comprendre leurs préférences
            2. Utilisez SEULEMENT les valeurs enum fournies ci-dessus - ne créez pas de nouvelles valeurs
            3. Comprenez les expressions françaises comme "avoir le coup de foudre", "chercher l'âme sœur", "relation sérieuse", "aventure", etc.
            4. Tenez compte de la culture française des rencontres (importance de la conversation, romantisme, etc.)
            5. Les tranches d'âge doivent être réalistes (ageRangeMin ≥ 18, ageRangeMax ≥ ageRangeMin)
            6. Les tranches de revenus doivent être en EUR et réalistes pour le contexte français
            7. Les tableaux peuvent contenir plusieurs valeurs le cas échéant
            8. Retournez SEULEMENT l'objet JSON, pas de texte supplémentaire ou de formatage markdown
            9. Concentrez-vous sur l'extraction des préférences des messages UTILISATEUR, pas des réponses IA
            10. Si l'utilisateur mentionne "FRENCH" ou parle français, incluez "FRENCH" dans preferredLanguages

            Extrayez ce que l'utilisateur recherche chez un partenaire et ses propres caractéristiques qui influencent ses préférences.
            Considérez les nuances culturelles françaises dans l'interprétation des préférences relationnelles.
            """

            # Call OpenAI API with configured model
            response = openai_client.chat.completions.create(
                model=config.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Vous êtes un expert en analyse de conversations de rencontres pour extraire les préférences utilisateur. Comprenez parfaitement le français et les nuances culturelles françaises. Retournez seulement du JSON valide correspondant exactement au format UserPreference avec les valeurs enum correctes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Lower temperature for more consistent results
                max_tokens=1500
            )

            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Clean up response if it has markdown formatting
            if ai_response.startswith("```json"):
                ai_response = ai_response[7:]
            if ai_response.endswith("```"):
                ai_response = ai_response[:-3]
            
            try:
                # Parse JSON response
                preferences_dict = json.loads(ai_response)
                
                # Validate and ensure all required fields are present with French-appropriate defaults
                default_preferences = {
                    "userId": data.user_id,
                    "interestedIn": ["FEMALE"],
                    "ageRangeMin": 22,
                    "ageRangeMax": 30,
                    "personalityTypes": ["INTROVERT"],
                    "drinking": "MAYBE",
                    "smoking": "NO",
                    "relationshipGoals": ["LONG_TERM"],
                    "religionPreference": ["OTHER"],
                    "educationPreference": ["BACHELORS"],
                    "lifestylePreferences": ["TRAVEL"],
                    "hasChildren": "NO",
                    "wantsChildren": "MAYBE",
                    "openToLongDistance": True,
                    "politicalView": "MODERATE",
                    "loveLanguage": ["QUALITY_TIME"],
                    "preferredLanguages": ["FRENCH"],
                    "incomeMin": 25000,
                    "incomeMax": 60000
                }
                
                # Merge AI results with defaults to ensure all fields are present
                for key, default_value in default_preferences.items():
                    if key not in preferences_dict or preferences_dict[key] is None:
                        preferences_dict[key] = default_value
                
                # Validate age ranges
                if preferences_dict["ageRangeMin"] < 18:
                    preferences_dict["ageRangeMin"] = 18
                if preferences_dict["ageRangeMax"] < preferences_dict["ageRangeMin"]:
                    preferences_dict["ageRangeMax"] = preferences_dict["ageRangeMin"] + 10
                
                return UserPreference(**preferences_dict)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing AI response as JSON: {e}")
                print(f"AI Response: {ai_response}")
                # Return French-appropriate default preferences if parsing fails
                return UserPreference(
                    userId=data.user_id,
                    interestedIn=["FEMALE"],
                    ageRangeMin=22,
                    ageRangeMax=30,
                    personalityTypes=["INTROVERT"],
                    drinking="MAYBE",
                    smoking="NO",
                    relationshipGoals=["LONG_TERM"],
                    religionPreference=["OTHER"],
                    educationPreference=["BACHELORS"],
                    lifestylePreferences=["TRAVEL"],
                    hasChildren="NO",
                    wantsChildren="MAYBE",
                    openToLongDistance=False,
                    politicalView="MODERATE",
                    loveLanguage=["QUALITY_TIME"],
                    preferredLanguages=["FRENCH"],
                    incomeMin=25000,
                    incomeMax=60000
                )
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # Return French-appropriate default preferences if API call fails
            return UserPreference(
                userId=data.user_id,
                interestedIn=["FEMALE"],
                ageRangeMin=22,
                ageRangeMax=30,
                personalityTypes=["INTROVERT"],
                drinking="MAYBE",
                smoking="NO",
                relationshipGoals=["LONG_TERM"],
                religionPreference=["OTHER"],
                educationPreference=["BACHELORS"],
                lifestylePreferences=["TRAVEL"],
                hasChildren="NO",
                wantsChildren="MAYBE",
                openToLongDistance=False,
                politicalView="MODERATE",
                loveLanguage=["QUALITY_TIME"],
                preferredLanguages=["FRENCH"],
                incomeMin=25000,
                incomeMax=60000
            )