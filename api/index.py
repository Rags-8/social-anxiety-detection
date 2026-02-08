from backend.main import app

# This is required for Vercel to recognize the entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
