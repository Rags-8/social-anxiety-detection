from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
from .database import init_db
from .models import AnalysisRequest, AnalysisResponse, ConversationModel
from .ml_utils import analyze_anxiety, start_model_preload
from .supabase_client import supabase
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
    init_db()
    # Pre-load ML models in background so first request isn't slow
    start_model_preload()

@app.get("/")
def read_root():
    return {"message": "Social Anxiety Detection API is running"}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_text(request: AnalysisRequest):
    result = analyze_anxiety(request.text)
    if not result:
        raise HTTPException(status_code=500, detail="Model not loaded or error in analysis")

    # Save to Supabase via REST API
    try:
        suggestions_payload = {
            "list": result["suggestions"],
            "confidence": result.get("confidence", 0.0)
        }

        data = {
            "user_text": request.text,
            "anxiety_level": result["anxiety_level"],
            "sentiment_score": result["sentiment_score"],
            "suggestions": json.dumps(suggestions_payload),
            "timestamp": datetime.now().isoformat()
        }
        
        # supabase.table().insert() returns data on success
        supabase.table("conversations").insert(data).execute()
        
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
        # Fetch the latest 50 conversations via Supabase REST API
        response = supabase.table("conversations").select("*").order("timestamp", desc=True).limit(50).execute()
        rows = response.data

        history_response = []
        for row in rows:
            try:
                suggestions_data = json.loads(row["suggestions"]) if row.get("suggestions") else []
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
                "id": row["id"],
                "user_text": row["user_text"],
                "anxiety_level": row["anxiety_level"],
                "sentiment_score": row["sentiment_score"],
                "suggestions": suggestions_list,
                "confidence": confidence_score,
                "timestamp": row["timestamp"]
            })
        return history_response
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

@app.get("/insights")
def get_insights():
    try:
        # Fetch all recent (e.g. last 1000) conversations to aggregate locally
        # Since Supabase standard REST API doesn't easily support raw GROUP BY SQL
        response = supabase.table("conversations").select("anxiety_level, timestamp").order("timestamp", desc=True).limit(1000).execute()
        rows = response.data

        # 1. Distribution counts & 2. Timeline by day
        dist_dict = {"High": 0, "Moderate": 0, "Low": 0}
        timeline_dict = {}

        for row in rows:
            level = row["anxiety_level"]
            if level in dist_dict:
                dist_dict[level] += 1
            
            # Format day as YYYY-MM-DD
            if row.get("timestamp"):
                day = row["timestamp"].split("T")[0]
                if day not in timeline_dict:
                    timeline_dict[day] = {"date": day, "Low": 0, "Moderate": 0, "High": 0}
                if level in timeline_dict[day]:
                    timeline_dict[day][level] += 1

        anxiety_distribution = [
            {"_id": level, "count": count}
            for level, count in dist_dict.items()
        ]

        # Sort timeline by date ascending for charts
        timeline = sorted(list(timeline_dict.values()), key=lambda x: x["date"])

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
        supabase.table("conversations").delete().eq("id", item_id).execute()
        return {"message": "Item deleted successfully"}
    except Exception as e:
        print(f"Error deleting history item: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete item")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False if os.environ.get("PORT") else True)
