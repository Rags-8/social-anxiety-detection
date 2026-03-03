# Social Anxiety Detection AI

A full-stack web application that detects social anxiety levels from user inputs using NLP and Machine Learning, providing empathetic suggestions and tracking history.

## Features
- **Real-time Anxiety Detection**: Classifies text as Low, Moderate, or High anxiety.
- **Empathetic AI Suggestions**: Provides tailored coping strategies.
- **Sentiment Analysis**: Tracks emotional tone of messages.
- **History & Insights**: Visualizes anxiety trends over time.

## Tech Stack
- **Backend**: Python, FastAPI, Motor (MongoDB), Scikit-learn, NLTK
- **Frontend**: React (Vite), Tailwind CSS, Recharts, Axios
- **Database**: MongoDB

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB installed and running locally

### 1. ML Model Training
```bash
# Install dependencies
pip install pandas numpy scikit-learn nltk

# Train model (ensure 'Combined Data.csv' is in root)
python train_model.py
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
Backend runs at `http://localhost:8000`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`.

## Usage
1. Open the frontend URL.
2. Go to "Chat" and describe your feelings.
3. View the analysis and suggestions.
4. Check "History" and "Insights" for progress.
