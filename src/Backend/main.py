#.\.venv\Scripts\python.exe -m uvicorn src.Backend.main:app --reload --port 8080


from fastapi import FastAPI

app = FastAPI(title="Bochen API")

@app.get("/health_check")
def health_check():
    return {
        "status": "ok"
    } 