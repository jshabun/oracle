"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import draft, players, team, recommendations, yahoo

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(yahoo.router, prefix="/yahoo", tags=["yahoo"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(team.router, prefix="/team", tags=["team"])
api_router.include_router(draft.router, prefix="/draft", tags=["draft"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
