from fastapi import FastAPI

from app.api.routes import admin, auth, users ,refresh_route

app = FastAPI(title="AuthGuard",version="1.0.0")


app.include_router(auth.router)
app.include_router(users.router, prefix="/auth")
app.include_router(refresh_route.router)
app.include_router(admin.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to AuthGuard API!"}


