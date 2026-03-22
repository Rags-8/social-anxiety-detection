from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json
import os
from datetime import datetime

# Adjust module imports
from .database import init_db, get_connection
from .models import PredictRequest, PredictResponse, HistoryItem
from .prediction_system import predict_with_words

# Use existing ml_utils to load the pickle model and clean text
from .ml_utils import get_model, clean_text, initialize_nltk

app = FastAPI(title="Social Anxiety Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Initialize SQLite database schema
    init_db()
    # Pre-load NLTK and the V3 model to guarantee fast requests
    initialize_nltk()
    get_model()

@app.get("/")
def read_root():
    return {"message": "Social Anxiety API running with Hybrid Word-Scoring system."}

@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(request: PredictRequest):
    model = get_model()
    if not model:
        raise HTTPException(status_code=500, detail="ML Model not loaded.")

    # 1. Base ML Prediction
    text_lower = request.text.lower()
    cleaned = clean_text(text_lower)
    
    if not cleaned:
        probs = [1.0, 0.0, 0.0] # Failsafe
    else:
        probs = model.predict_proba([cleaned])[0]
        
    pred_idx = np.argmax(probs)
    ml_conf = float(np.max(probs))
    
    label_map = {0: "Low Anxiety", 1: "Moderate Anxiety", 2: "High Anxiety"}
    ml_prediction = label_map[pred_idx]
    
    # 2. Enhanced Word Scoring Pass
    final_output = predict_with_words(request.text, ml_prediction, ml_conf)
    
    # Format DB saving details depending on output
    pred_val = final_output.get("prediction", "Uncertain")
    conf_val = final_output.get("confidence", 0.0)
    dw_val = json.dumps(final_output.get("detected_words", []))
    
    # If the response doesn't have a generated timestamp due to Uncertain fallback, make one
    ts_val = final_output.get("timestamp", datetime.utcnow().isoformat())

    # 3. Save to SQLite Database
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO predictions (text, prediction, confidence, detected_words, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (request.text, pred_val, conf_val, dw_val, ts_val))
            conn.commit()
        except Exception as e:
            print(f"Error saving to SQLite: {e}")
        finally:
            conn.close()

    return final_output

@app.get("/history", response_model=list[HistoryItem])
def get_history():
    """Returns the last 20 predictions from the database."""
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error.")
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 20")
        rows = cur.fetchall()
        
        history_list = []
        for row in rows:
            history_list.append({
                "id": row["id"],
                "text": row["text"],
                "prediction": row["prediction"],
                "confidence": row["confidence"],
                "detected_words": json.loads(row["detected_words"]),
                "timestamp": row["timestamp"]
            })
        return history_list
    except Exception as e:
        print(f"Error fetching SQLite history: {e}")
        return []
    finally:
        conn.close()

@app.delete("/history/{item_id}")
def delete_history_item(item_id: int):
    """Deletes a specific prediction from the database."""
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error.")
        
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM predictions WHERE id = ?", (item_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found.")
        conn.commit()
        return {"message": "Conversation deleted successfully."}
    except Exception as e:
        print(f"Error deleting history item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    finally:
        conn.close()

@app.get("/insights")
def get_insights():
    """Aggregates anxiety levels and daily trends for visualization."""
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error.")
    try:
        cur = conn.cursor()
        
        # 1. Total Distribution
        cur.execute("SELECT prediction, COUNT(*) as count FROM predictions GROUP BY prediction")
        dist_rows = cur.fetchall()
        
        distribution = []
        for row in dist_rows:
            label = row["prediction"].replace(" Anxiety", "")
            distribution.append({
                "_id": label,
                "count": row["count"]
            })

        # 2. Daily Trends (Variation over time)
        # Using SQLite date() function to group by day
        cur.execute("""
            SELECT date(timestamp) as day, 
                   COUNT(CASE WHEN prediction = 'High Anxiety' THEN 1 END) as High,
                   COUNT(CASE WHEN prediction = 'Moderate Anxiety' THEN 1 END) as Moderate,
                   COUNT(CASE WHEN prediction = 'Low Anxiety' THEN 1 END) as Low
            FROM predictions 
            GROUP BY day 
            ORDER BY day ASC
            LIMIT 14
        """)
        trend_rows = cur.fetchall()
        
        trends = []
        for row in trend_rows:
            trends.append({
                "day": row["day"],
                "High": row["High"],
                "Moderate": row["Moderate"],
                "Low": row["Low"]
            })
            
        return {
            "anxiety_distribution": distribution,
            "daily_trends": trends
        }
    except Exception as e:
        print(f"Error calculating insights: {e}")
        return {"anxiety_distribution": [], "daily_trends": []}
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
