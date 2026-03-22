from pydantic import BaseModel
from typing import List, Optional

class DetectedWord(BaseModel):
    word: str
    label: str
    weight: int

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    prediction: str
    confidence: Optional[float] = None
    reason: Optional[str] = None
    detected_words: Optional[List[DetectedWord]] = None
    timestamp: Optional[str] = None
    suggestion: Optional[str] = None
    follow_up: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class HistoryItem(BaseModel):
    id: int
    text: str
    prediction: str
    confidence: float
    detected_words: List[DetectedWord]
    timestamp: str
