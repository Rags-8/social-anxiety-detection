from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    anxiety_level: str
    sentiment_score: float
    explanation: str
    suggestions: List[str]
    confidence: float

class ConversationModel(BaseModel):
    id: Optional[int] = None
    user_text: str
    anxiety_level: str
    sentiment_score: float
    suggestions: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_text": "I feel nervous.",
                "anxiety_level": "Low",
                "sentiment_score": -0.1,
                "suggestions": ["Take a deep breath."],
                "timestamp": "2023-10-27T10:00:00"
            }
        }
