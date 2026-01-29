from fastapi import FastAPI

app = FastAPI(title="AuthGuard",version="1.0.0")

@app.get("/")
async def read_root():
    return {"message": "Welcome to AuthGuard API!"}