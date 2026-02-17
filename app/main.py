from fastapi import FastAPI

from app.api.routes import admin, auth, users ,refresh_route
from app.core.seed_roles import seed_roles

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import async_session_maker
from app.core.seed_roles import seed_roles

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with async_session_maker() as session:
        await seed_roles(session)

    yield


app = FastAPI(title="AuthGuard",version="1.0.0", lifespan=lifespan)


app.include_router(auth.router)
app.include_router(users.router, prefix="/auth")
app.include_router(refresh_route.router)
app.include_router(admin.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to AuthGuard API!"}


