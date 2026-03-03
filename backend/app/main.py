from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
from .database import get_connection, init_db
from .models import AnalysisRequest, AnalysisResponse, ConversationModel
from .ml_utils import analyze_anxiety
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database init failed at startup: {e}. Continuing without DB.")

@app.get("/")
def read_root():
    return {"message": "Social Anxiety Detection API is running"}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_text(request: AnalysisRequest):
    result = analyze_anxiety(request.text)
    if not result:
        raise HTTPException(status_code=500, detail="Model not loaded or error in analysis")

    # Save to PostgreSQL
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (user_text, anxiety_level, sentiment_score, suggestions, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    request.text,
                    result["anxiety_level"],
                    result["sentiment_score"],
                    result["suggestions"],  # Constant list/array for TEXT[]
                    datetime.utcnow()
                )
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving to DB: {e}")

    return AnalysisResponse(
        anxiety_level=result["anxiety_level"],
        sentiment_score=result["sentiment_score"],
        explanation=f"Detected anxiety level: {result['anxiety_level']}",
        suggestions=result["suggestions"],
        confidence=result["confidence"]
    )

from fastapi.responses import JSONResponse
import json

@app.get("/history")
def get_history():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, user_text, anxiety_level, sentiment_score, suggestions, timestamp FROM conversations ORDER BY timestamp DESC LIMIT 50"
            )
            rows = cur.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "user_text": row[1],
                "anxiety_level": row[2],
                "sentiment_score": row[3],
                "suggestions": json.loads(row[4]) if isinstance(row[4], str) else (row[4] or []),
                "timestamp": row[5].isoformat() if hasattr(row[5], 'isoformat') else str(row[5])
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

@app.get("/insights")
def get_insights():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT anxiety_level, COUNT(*) as count, AVG(sentiment_score) as avg_sentiment
                FROM conversations
                GROUP BY anxiety_level
                """
            )
            rows = cur.fetchall()
        conn.close()
        return {
            "anxiety_distribution": [
                {"_id": row[0], "count": row[1], "avg_sentiment": row[2]}
                for row in rows
            ]
        }
    except Exception as e:
        print(f"Error fetching insights: {e}")
        return {"anxiety_distribution": []}

@app.delete("/history/{item_id}")
def delete_history_item(item_id: int):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM conversations WHERE id = %s", (item_id,))
        conn.commit()
        conn.close()
        return {"message": "Item deleted successfully"}
    except Exception as e:
        print(f"Error deleting history item: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete item")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
