# MindCare AI - Social Anxiety Detection

A full-stack web application that uses machine learning to detect social anxiety levels from conversational text and provides helpful suggestions.

## Features
- **Real-time Anxiety Prediction**: Analyzes user input to predict Low, Moderate, or High anxiety using a Multinomial Naive Bayes model.
- **Automatic History Saving**: Every conversation is automatically saved to the database.
- **Conversational Interface**: Chat with an AI that offers empathetic responses and coping strategies.
- **History & Insights**: View past conversations and anxiety trends over time.
- **Modern UI**: Clean, responsive dark-themed interface with Home, Chat, History and Insights views.

## Tech Stack
- **Frontend**: React (Vite), CSS Modules, Recharts, Lucide Icons
- **Backend**: Python FastAPI, NLTK, Scikit-learn
- **Database**: MongoDB (`mindcare_db`, `chats` collection)
- **ML Model**: Multinomial Naive Bayes with TF-IDF Vectorization

## Prerequisites
- **Python 3.8+**
- **Node.js 16+** & **npm**
- **MongoDB** (Running locally on default port 27017)

## Installation

1. **Clone/Download the repository**.
2. **Install Backend Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Ensure `scikit-learn`, `pandas`, `nltk`, `fastapi`, `uvicorn`, `pymongo` are installed.*

3. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

4. **Train the Model**:
   Ensure `Combined Data.csv` is in your Downloads folder (or update `train_model.py`).
   ```bash
   python train_model.py
   ```

## Running the App

### Option 1: One-Click Script (Windows)
Double-click `run_app.bat` to start both backend and frontend servers.

### Option 2: Manual Start
**Backend**:
```bash
cd backend
uvicorn main:app --reload
```
API runs at: `http://localhost:8000`

**Frontend**:
```bash
cd frontend
npm run dev
```
UI runs at: `http://localhost:5173`

## Usage
1. Open the web app.
2. Click "Start Chatting Now" from the Home screen.
3. Type how you are feeling in the chat.
4. Receive anxiety analysis and suggestions.
5. Check "History" for past chats or "Insights" for trends.

## Disclaimer
This project is for educational purposes only. It is **not** a medical diagnosis tool. If you are in crisis, please contact professional mental health services.

Public Url : https://social-anxiety-123.streamlit.app/
