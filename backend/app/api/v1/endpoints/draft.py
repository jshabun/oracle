"""
Draft mode endpoints
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Dict, Any, List, Optional

from app.services.yahoo_fantasy import YahooFantasyService, YahooOAuthError, YahooAPIError
from app.services.player_data_service import PlayerDataService
from app.core.config import settings

router = APIRouter()


# Dependency to get services
_yahoo_service: Optional[YahooFantasyService] = None
_player_service: Optional[PlayerDataService] = None


def get_yahoo_service() -> YahooFantasyService:
    """Get or create Yahoo Fantasy service instance"""
    global _yahoo_service
    if _yahoo_service is None:
        _yahoo_service = YahooFantasyService()
    return _yahoo_service


def get_player_service(
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> PlayerDataService:
    """Get or create Player Data service instance"""
    global _player_service
    if _player_service is None:
        _player_service = PlayerDataService(yahoo)
    return _player_service


# In-memory draft sessions (TODO: Move to database)
_draft_sessions: Dict[str, Dict[str, Any]] = {}


@router.post("/start")
async def start_draft_session(
    league_key: str = Query(..., description="League key (e.g., nba.l.12345)"),
    draft_position: int = Query(..., description="Your draft position (1-10)"),
    snake: bool = Query(True, description="Snake draft format")
) -> Dict[str, Any]:
    """Start a new draft session"""
    import uuid
    
    session_id = str(uuid.uuid4())
    
    _draft_sessions[session_id] = {
        "session_id": session_id,
        "league_key": league_key,
        "draft_position": draft_position,
        "snake": snake,
        "num_teams": 10,  # TODO: Get from league settings
        "current_round": 1,
        "roster": [],
        "punt_categories": [],
        "status": "active"
    }
    
    return _draft_sessions[session_id]


@router.get("/recommendations")
async def get_draft_recommendations(
    session_id: str = Query(..., description="Draft session ID"),
    league_key: Optional[str] = Query(None, description="League key (if no session)"),
    limit: int = Query(10, description="Number of recommendations"),
    player_service: PlayerDataService = Depends(get_player_service)
) -> Dict[str, Any]:
    """
    Get draft pick recommendations
    
    Returns top available players ranked by:
    - Overall Z-score value
    - Positional scarcity
    - Fit with existing roster (if session provided)
    - Punt strategy detection
    """
    try:
        # Get session context
        current_roster = []
        punt_categories = []
        session_league_key = league_key
        
        if session_id in _draft_sessions:
            session = _draft_sessions[session_id]
            current_roster = session.get("roster", [])
            punt_categories = session.get("punt_categories", [])
            session_league_key = session.get("league_key")
        elif not league_key:
            raise HTTPException(
                status_code=400,
                detail="Either session_id or league_key must be provided"
            )
        
        # Get recommendations from service
        recommendations = await player_service.get_draft_recommendations(
            league_key=session_league_key,
            current_roster=current_roster,
            punt_categories=punt_categories,
            limit=limit
        )
        
        return {
            "session_id": session_id,
            "league_key": session_league_key,
            "recommendations": recommendations,
            "count": len(recommendations),
            "context": {
                "roster_size": len(current_roster),
                "punting": punt_categories,
                "categories": settings.CATEGORIES
            }
        }
        
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


@router.post("/pick")
async def record_pick(
    session_id: str,
    player_id: str,
    player_name: str,
    pick_number: int,
    round: int,
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Record a draft pick
    
    Updates session state to track:
    - Players on your roster (if your pick)
    - Detected punt strategy
    - Positional needs
    """
    if session_id not in _draft_sessions:
        raise HTTPException(status_code=404, detail="Draft session not found")
    
    session = _draft_sessions[session_id]
    
    pick_info = {
        "player_id": player_id,
        "player_name": player_name,
        "pick_number": pick_number,
        "round": round,
        "team_id": team_id,
        "is_my_pick": team_id is None  # If no team_id specified, assume user's pick
    }
    
    # Add to roster if this is the user's pick
    if pick_info["is_my_pick"]:
        session["roster"].append(pick_info)
        session["current_round"] = round
        
        # TODO: Recalculate punt strategy based on roster
    
    return {
        "success": True,
        "session_id": session_id,
        "pick_recorded": pick_info,
        "roster_size": len(session["roster"])
    }


@router.get("/board")
async def get_draft_board(session_id: str) -> Dict[str, Any]:
    """Get current draft board state"""
    if session_id not in _draft_sessions:
        raise HTTPException(status_code=404, detail="Draft session not found")
    
    session = _draft_sessions[session_id]
    
    return {
        "session_id": session_id,
        "draft_position": session["draft_position"],
        "current_round": session["current_round"],
        "roster": session["roster"],
        "punt_categories": session["punt_categories"],
        "status": session["status"]
    }


@router.get("/session/{session_id}")
async def get_draft_session(session_id: str) -> Dict[str, Any]:
    """Get current draft session state"""
    if session_id not in _draft_sessions:
        raise HTTPException(status_code=404, detail="Draft session not found")
    
    return _draft_sessions[session_id]


@router.delete("/session/{session_id}")
async def delete_draft_session(session_id: str) -> Dict[str, Any]:
    """Delete a draft session"""
    if session_id not in _draft_sessions:
        raise HTTPException(status_code=404, detail="Draft session not found")
    
    del _draft_sessions[session_id]
    
    return {"status": "deleted", "session_id": session_id}
