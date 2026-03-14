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

# CORS - Allow all origins for production compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    # Save to SQLite
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # We smartly encode 'confidence' inside 'suggestions' to avoid modifying the DB schema
        suggestions_payload = {
            "list": result["suggestions"],
            "confidence": result.get("confidence", 0.0)
        }
        
        cur.execute(
            """
            INSERT INTO conversations (user_text, anxiety_level, sentiment_score, suggestions, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.text,
                result["anxiety_level"],
                result["sentiment_score"],
                json.dumps(suggestions_payload),
                datetime.now().isoformat() # Use local time as requested
            )
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving to DB: {e}")

    return AnalysisResponse(
        anxiety_level=result["anxiety_level"],
        sentiment_score=result["sentiment_score"],
        explanation=result.get("explanation", f"Detected anxiety level: {result['anxiety_level']}"),
        suggestions=result["suggestions"],
        confidence=result["confidence"]
    )

@app.get("/history")
def get_history():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user_text, anxiety_level, sentiment_score, suggestions, timestamp FROM conversations ORDER BY timestamp DESC LIMIT 50"
        )
        rows = cur.fetchall()
        conn.close()
        history_response = []
        for row in rows:
            try:
                suggestions_data = json.loads(row[4]) if row[4] else []
                if isinstance(suggestions_data, dict):
                    suggestions_list = suggestions_data.get("list", [])
                    confidence_score = suggestions_data.get("confidence", 0.0)
                else:
                    suggestions_list = suggestions_data
                    confidence_score = 0.0
            except:
                suggestions_list = []
                confidence_score = 0.0

            history_response.append({
                "id": row[0],
                "user_text": row[1],
                "anxiety_level": row[2],
                "sentiment_score": row[3],
                "suggestions": suggestions_list,
                "confidence": confidence_score,
                "timestamp": row[5]
            })
        return history_response
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

@app.get("/insights")
def get_insights():
    try:
        conn = get_connection()
        cur = conn.cursor()
        # 1. Bar Chart Data (確保 High, Moderate, Low 都有)
        cur.execute(
            """
            SELECT anxiety_level, COUNT(*) as count
            FROM conversations
            WHERE anxiety_level IN ('High', 'Moderate', 'Low')
            GROUP BY anxiety_level
            """
        )
        dist_rows = cur.fetchall()
        
        # 2. Line Chart Data (Trend over time by day)
        cur.execute(
            """
            SELECT date(timestamp) as day, anxiety_level, COUNT(*) as count
            FROM conversations
            WHERE anxiety_level IN ('High', 'Moderate', 'Low')
            GROUP BY date(timestamp), anxiety_level
            ORDER BY date(timestamp) ASC
            """
        )
        trend_rows = cur.fetchall()
        conn.close()
        
        # Ensure all categories exist in distribution
        dist_dict = {"High": 0, "Moderate": 0, "Low": 0}
        for level, count in dist_rows:
            dist_dict[level] = count
            
        anxiety_distribution = [
            {"_id": level, "count": count}
            for level, count in dist_dict.items()
        ]
        
        # Process Timeline
        timeline_dict = {}
        for row in trend_rows:
            day, level, count = row
            if day not in timeline_dict:
                timeline_dict[day] = {"date": day, "Low": 0, "Moderate": 0, "High": 0}
            timeline_dict[day][level] = count
            
        timeline = list(timeline_dict.values())

        return {
            "anxiety_distribution": anxiety_distribution,
            "timeline": timeline
        }
    except Exception as e:
        print(f"Error fetching insights: {e}")
        return {"anxiety_distribution": [], "timeline": []}

@app.delete("/history/{item_id}")
def delete_history_item(item_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM conversations WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return {"message": "Item deleted successfully"}
    except Exception as e:
        print(f"Error deleting history item: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete item")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False if os.environ.get("PORT") else True)
