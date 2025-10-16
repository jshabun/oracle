from fastapi import APIRouter

router = APIRouter(prefix="/draft", tags=["draft"])

@router.get("/recommendations")
async def draft_recommendations(leagueKey: str, punt: str | None = None):
    # TODO: pull available players for leagueKey via Yahoo, compute z-scores
    # For now, return placeholder
    return {"leagueKey": leagueKey, "players": []}