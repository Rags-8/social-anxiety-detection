import random
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import numpy as np
from datetime import datetime
from .database import chats_collection as chat_collection, chat_helper, delete_chat

app = FastAPI()


# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:5177",
    "http://localhost:5178",
    "http://localhost:5179",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity in this project deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model and Vectorizer
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "anxiety_model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "models", "tfidf_vectorizer.pkl")

model = None
vectorizer = None

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("Model and Vectorizer loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

# Data Models
class UserInput(BaseModel):
    text: str
    user_id: str = "guest"

class ChatResponse(BaseModel):
    anxiety_level: str
    explanation: str
    suggestions: list[str]

# Suggestions Logic (Dynamic Pools)
suggestions_db = {
    "Low Anxiety": [
        [
            "Great to hear you are feeling okay!",
            "Maintain your routine and stay hydrated.",
            "Keep practicing mindfulness to stay balanced."
        ],
        [
            "It's wonderful that you're in a good place.",
            "Take a moment to appreciate this feeling.",
            "Engage in a hobby you enjoy to keep the momentum."
        ],
        [
            "You seem to be handling things well.",
            "Continue your positive habits.",
            "Maybe reach out to a friend just to say hi."
        ],
        [
            "Stability is key, keep it up!",
            "Ensure you're getting enough sleep.",
            "A short walk outside can be lovely today."
        ]
    ],
    "Moderate Anxiety": [
        [
            "Try some deep breathing exercises (4-7-8 technique).",
            "Take a short walk or break to clear your mind.",
            "Practice grounding techniques like identifying 5 things you see.",
            "Listen to calming music."
        ],
        [
            "Acknowledge your feelings without judgment.",
            "Step away from screens for 10 minutes.",
            "Focus on a task you can control right now.",
            "Drink a glass of water slowly."
        ],
        [
            "Progressive muscle relaxation might help.",
            "Write down what's worrying you to get it out of your head.",
            "Talk to someone you trust about how you feel.",
            "Limit caffeine intake for the rest of the day."
        ],
        [
            "Visualize a calm, safe place.",
            "Do a quick 5-minute meditation.",
            "Stretch your body to release tension.",
            "Remind yourself: 'This too shall pass'."
        ]
    ],
    "High Anxiety": [
        [
            "Please consider reaching out to a mental health professional.",
            "Connect with a trusted friend or family member immediately.",
            "Practice deep grounding exercises.",
            "Remember, this feeling is temporary and you are not alone."
        ],
        [
            "If you feel unsafe, please contact emergency services.",
            "Focus strictly on your breathing right now.",
            "Find a quiet space to decompress immediately.",
            "Do not hesitate to ask for help."
        ],
        [
            "Your well-being is the priority right now.",
            "Try the 5-4-3-2-1 grounding technique.",
            "Call a helpline if you need immediate support.",
            "Be kind to yourself; this is a tough moment."
        ],
        [
            "Reach out to a support network.",
            "Avoid isolating yourself completely.",
            "Focus on getting through the next hour.",
            "Professional support can make a huge difference."
        ]
    ]
}

# Topic-Specific Suggestions
topic_suggestions = {
    "Sleep": {
        "keywords": ["sleep", "insomnia", "awake", "tired", "bed", "night", "waking"],
        "suggestions": [
            "Try a 'brain dump' journal before bed to clear your mind.",
            "Avoid screens for at least an hour before sleeping.",
            "Focus on keeping a consistent sleep schedule."
        ]
    },
    "Work": {
        "keywords": ["work", "job", "boss", "deadline", "career", "presentation", "meeting"],
        "suggestions": [
            "Break large tasks into small, manageable steps.",
            "Take short 5-minute breaks every hour to reset.",
            "Communicate your capacity clearly to your team."
        ]
    },
    "Social": {
        "keywords": ["party", "crowd", "people", "talk", "social", "meeting", "friends", "date"],
        "suggestions": [
            "Focus on listening rather than what to say next.",
            "It's okay to take a break and step outside for a moment.",
            "Remember that most people are focused on themselves."
        ]
    },
    "School": {
        "keywords": ["exam", "test", "study", "grade", "school", "class", "fail"],
        "suggestions": [
            "Use the Pomodoro technique for focused study sessions.",
            "Don't hesitate to ask a teacher or peer for clarification.",
            "Remember that one grade doesn't define your future."
        ]
    },
    "Panic": {
        "keywords": ["panic", "heart", "breath", "dizzy", "dying", "attack", "scared"],
        "suggestions": [
            "Focus on long, slow exhales to calm your nervous system.",
            "Name 5 things you can see and 4 things you can touch.",
            "This feeling is uncomfortable, but it will pass."
        ]
    }
}

def get_suggestions(level, text=""):
    suggestions = []
    
    # Check for topics in text
    text_lower = text.lower()
    for topic, data in topic_suggestions.items():
        if any(keyword in text_lower for keyword in data["keywords"]):
            suggestions.extend(data["suggestions"])
    
    # Get general suggestions for the level
    general_options = suggestions_db.get(level, [])
    if general_options:
         # If no topic found, just take a full random set
         if not suggestions:
             suggestions = random.choice(general_options)
         else:
             # If topics found, add 1-2 general ones to mix
             random_general = random.choice(general_options)
             # Take first 2 from general to keep it concise
             suggestions.extend(random_general[:2])
    
    # Ensure unique and limited
    final_suggestions = list(set(suggestions))
    return final_suggestions[:4]  # Return max 4 suggestions

def clean_text(text):
    import re
    from nltk.stem import WordNetLemmatizer
    # fast cleaning for inference
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower().strip()
    return text

def check_harmful_content(text):
    harmful_keywords = ["suicide", "kill myself", "die", "hurt myself", "death", "end my life"]
    text_lower = text.lower()
    for keyword in harmful_keywords:
        if keyword in text_lower:
            return True
    return False

@app.get("/")
async def root():
    return {"message": "Social Anxiety Detection API is running"}

@app.post("/predict", response_model=ChatResponse)
async def predict_anxiety(input_data: UserInput = Body(...)):
    # 1. Harmful Content Check
    if check_harmful_content(input_data.text):
        return {
            "anxiety_level": "High Anxiety",
            "explanation": "I am really concerned about what you're sharing. Please prioritize your safety and reach out to a professional immediately.",
            "suggestions": [
                 "Call 988 Suicide & Crisis Lifeline (or your local emergency number)",
                 "Go to the nearest emergency room",
                 "Connect with a trusted friend or family member immediately."
            ]
        }

    if not model or not vectorizer:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    clean_input = clean_text(input_data.text)
    
    if not clean_input:
         raise HTTPException(status_code=400, detail="Input text is empty or invalid")

    # Vectorize
    vectorized_text = vectorizer.transform([clean_input])
    
    # Predict
    prediction = model.predict(vectorized_text)[0]
    
    # Logic to refine anxiety level based on probability if needed
    # For now, stick to the model's mapped prediction
    anxiety_level = prediction
    
    # Pass clean_input to get topic-specific suggestions
    suggestions = get_suggestions(anxiety_level, clean_input)
    
    # Empathetic Explanation (Dynamic)
    empathy_map = {
        "Low Anxiety": [
            "It sounds like you are in a good headspace.",
            "I'm glad to see you're feeling balanced.",
            "It seems like you're having a positive day.",
            "That sounds like a healthy outlook."
        ],
        "Moderate Anxiety": [
            "It is completely normal to feel this way sometimes.",
            "You might be feeling a bit overwhelmed, and that's okay.",
            "It sounds like things are a little stressful right now.",
            "Be gentle with yourself as you navigate these feelings."
        ],
        "High Anxiety": [
            "Please remember that this feeling is temporary and you are not alone.",
            "It sounds like you're going through a really tough time.",
            "I hear how difficult things are for you right now.",
            "It's brave of you to share how much you're struggling."
        ]
    }
    
    # Randomly select a phrase
    phrases = empathy_map.get(anxiety_level, [""])
    phrase = random.choice(phrases) if phrases else ""
    
    explanation = f"Based on your input, the model predicts {anxiety_level}. {phrase}"

    # AUTOSAVE: Save chat history to MongoDB
    try:
        chat_entry = {
            "user_id": input_data.user_id,
            "message": input_data.text,
            "response": explanation,
            "anxiety_level": anxiety_level,
            "suggestions": suggestions,
            "timestamp": datetime.utcnow()
        }
        chat_collection.insert_one(chat_entry)
    except Exception as e:
        print(f"Error autosaving chat: {e}")
    
    return {
        "anxiety_level": anxiety_level,
        "explanation": explanation,
        "suggestions": suggestions
    }

class SaveChatRequest(BaseModel):
    user_id: str
    message: str
    response: str
    anxiety_level: str
    suggestions: list[str]

@app.post("/history")
async def save_chat(chat_data: SaveChatRequest):
    try:
        chat_entry = chat_data.dict()
        chat_entry["timestamp"] = datetime.utcnow()
        
        # Synchronous insert
        result = chat_collection.insert_one(chat_entry)
        print(f"DEBUG: Saved chat with ID: {result.inserted_id}") # Minimal logging
        
        return {"message": "Chat saved successfully", "id": str(result.inserted_id)}
    except Exception as e:
        print(f"ERROR: Failed to save chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    chats = []
    try:
        # Synchronous find
        for chat in chat_collection.find({"user_id": user_id}):
            chats.append(chat_helper(chat))
    except Exception as e:
        print(f"ERROR: Failed to fetch history: {e}")
    return chats

@app.delete("/history/{chat_id}")
async def delete_history_record(chat_id: str):
    try:
        # Synchronous delete
        deleted = delete_chat(chat_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Record not found or invalid ID")
        print(f"DEBUG: Deleted chat with ID: {chat_id}") # Minimal logging
        return {"message": "Record deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"ERROR: Database Delete Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New Endpoints as requested
@app.get("/get_chats/{user_id}")
async def get_chats(user_id: str):
    return await get_history(user_id)

@app.delete("/delete_chat/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    return await delete_history_record(chat_id)

@app.get("/get_insights/{user_id}")
async def get_insights(user_id: str):
    chats = await get_history(user_id)
    low = 0
    moderate = 0
    high = 0
    
    for chat in chats:
        level = chat.get("anxiety_level", "")
        if "Low" in level:
            low += 1
        elif "Moderate" in level:
            moderate += 1
        elif "High" in level:
            high += 1
            
    return {
        "low": low,
        "moderate": moderate,
        "high": high
    }
