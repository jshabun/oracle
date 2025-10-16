from fastapi import FastAPI
from .oauth.routes import router as yahoo_auth
from .routers.draft import router as draft_router

app = FastAPI(title="Fantasy Assistant API")

app.include_router(yahoo_auth, prefix="/api/auth")
app.include_router(draft_router, prefix="/api")

@app.get("/api/health")
async def health():
    return {"ok": True}