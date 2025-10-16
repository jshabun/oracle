"""
Yahoo Fantasy API integration
"""
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import Dict, Any, List, Optional

from app.services.yahoo_fantasy import YahooFantasyService, YahooOAuthError, YahooAPIError
from app.core.config import settings

router = APIRouter()


# Dependency to get Yahoo service
# In production, you'd want to manage tokens per user in a database
_yahoo_service: Optional[YahooFantasyService] = None


def get_yahoo_service() -> YahooFantasyService:
    """Get or create Yahoo Fantasy service instance"""
    global _yahoo_service
    if _yahoo_service is None:
        _yahoo_service = YahooFantasyService()
    return _yahoo_service


@router.get("/auth/url")
async def get_auth_url(
    redirect_uri: str = Query(
        default="http://localhost:8000/api/v1/yahoo/callback",
        description="OAuth callback URL"
    )
) -> Dict[str, str]:
    """
    Get Yahoo OAuth authorization URL
    
    User should visit this URL to authorize the application
    """
    try:
        yahoo = get_yahoo_service()
        auth_url = yahoo.get_authorization_url(redirect_uri)
        
        return {
            "auth_url": auth_url,
            "redirect_uri": redirect_uri,
            "instructions": "Visit the auth_url to authorize the application"
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Yahoo"),
    redirect_uri: str = Query(
        default="http://localhost:8000/api/v1/yahoo/callback",
        description="Redirect URI used in authorization"
    )
) -> Dict[str, str]:
    """
    OAuth callback endpoint
    
    Yahoo redirects here after user authorizes the application
    """
    try:
        yahoo = get_yahoo_service()
        token_data = await yahoo.exchange_code_for_token(code, redirect_uri)
        
        return {
            "status": "success",
            "message": "Authorization successful! You can now use the API.",
            "expires_in": str(token_data.get("expires_in", 0)) + " seconds"
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=400, detail=f"Authorization failed: {str(e)}")


@router.get("/leagues")
async def get_user_leagues(
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Get all leagues for authenticated user"""
    try:
        leagues = await yahoo.get_user_leagues(sport="nba")
        
        # Extract key information
        league_list = []
        for league in leagues:
            league_info = {
                "league_key": league.get("league_key"),
                "league_id": league.get("league_id"),
                "name": league.get("name"),
                "season": league.get("season"),
                "num_teams": league.get("num_teams"),
                "current_week": league.get("current_week"),
                "start_week": league.get("start_week"),
                "end_week": league.get("end_week")
            }
            league_list.append(league_info)
        
        return {
            "leagues": league_list,
            "count": len(league_list)
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/league/{league_key}/settings")
async def get_league_settings(
    league_key: str,
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Get league settings and configuration"""
    try:
        settings_data = await yahoo.get_league_settings(league_key)
        return {
            "league_key": league_key,
            "settings": settings_data
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/league/{league_key}/standings")
async def get_league_standings(
    league_key: str,
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Get league standings"""
    try:
        standings = await yahoo.get_league_standings(league_key)
        
        # Extract key information
        teams = []
        for team in standings:
            team_info = {
                "team_key": team.get("team_key"),
                "team_id": team.get("team_id"),
                "name": team.get("name"),
                "rank": team[1].get("team_standings", {}).get("rank") if len(team) > 1 else None,
                "wins": team[1].get("team_standings", {}).get("outcome_totals", {}).get("wins") if len(team) > 1 else None,
                "losses": team[1].get("team_standings", {}).get("outcome_totals", {}).get("losses") if len(team) > 1 else None,
                "ties": team[1].get("team_standings", {}).get("outcome_totals", {}).get("ties") if len(team) > 1 else None,
            }
            teams.append(team_info)
        
        return {
            "league_key": league_key,
            "standings": teams
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/league/{league_key}/players/available")
async def get_available_players(
    league_key: str,
    position: Optional[str] = Query(None, description="Filter by position"),
    start: int = Query(0, description="Starting index"),
    count: int = Query(25, description="Number of players to return"),
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Get available players in the league"""
    try:
        players = await yahoo.get_available_players(
            league_key=league_key,
            position=position,
            start=start,
            count=count
        )
        
        # Extract key player information
        player_list = []
        for player in players:
            player_info = {
                "player_key": player.get("player_key"),
                "player_id": player.get("player_id"),
                "name": player.get("name", {}).get("full"),
                "first_name": player.get("name", {}).get("first"),
                "last_name": player.get("name", {}).get("last"),
                "positions": player.get("eligible_positions"),
                "team": player.get("editorial_team_abbr"),
                "status": player.get("status"),
            }
            player_list.append(player_info)
        
        return {
            "league_key": league_key,
            "players": player_list,
            "count": len(player_list),
            "start": start
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/league/{league_key}/players/search")
async def search_players(
    league_key: str,
    query: str = Query(..., description="Player name to search"),
    start: int = Query(0, description="Starting index"),
    count: int = Query(25, description="Number of results"),
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Search for players by name"""
    try:
        players = await yahoo.search_players(
            league_key=league_key,
            search_term=query,
            start=start,
            count=count
        )
        
        # Extract key player information
        player_list = []
        for player in players:
            player_info = {
                "player_key": player.get("player_key"),
                "player_id": player.get("player_id"),
                "name": player.get("name", {}).get("full"),
                "positions": player.get("eligible_positions"),
                "team": player.get("editorial_team_abbr"),
            }
            player_list.append(player_info)
        
        return {
            "query": query,
            "players": player_list,
            "count": len(player_list)
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team/{team_key}/roster")
async def get_team_roster(
    team_key: str,
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Get team roster"""
    try:
        players = await yahoo.get_team_roster(team_key)
        
        # Extract key player information
        player_list = []
        for player in players:
            player_info = {
                "player_key": player.get("player_key"),
                "player_id": player.get("player_id"),
                "name": player.get("name", {}).get("full"),
                "positions": player.get("eligible_positions"),
                "selected_position": player.get("selected_position", {}).get("position") if len(player) > 1 else None,
                "team": player.get("editorial_team_abbr"),
                "status": player.get("status"),
            }
            player_list.append(player_info)
        
        return {
            "team_key": team_key,
            "roster": player_list,
            "count": len(player_list)
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team/{team_key}/matchup")
async def get_team_matchup(
    team_key: str,
    week: Optional[int] = Query(None, description="Week number (current week if not specified)"),
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Get team's matchup for a specific week"""
    try:
        matchup_data = await yahoo.get_team_matchup(team_key, week)
        
        return {
            "team_key": team_key,
            "matchup": matchup_data
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/player/{player_key}/stats")
async def get_player_stats(
    player_key: str,
    stat_type: str = Query("season", description="Type of stats (season, week, etc.)"),
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Get player statistics"""
    try:
        stats_data = await yahoo.get_player_stats(player_key, stat_type)
        
        return {
            "player_key": player_key,
            "stat_type": stat_type,
            "stats": stats_data
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tokens/status")
async def get_token_status(
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, Any]:
    """Get current authentication status"""
    tokens = yahoo.get_tokens()
    
    return {
        "authenticated": tokens["access_token"] is not None,
        "expires_at": tokens["expires_at"],
        "has_refresh_token": tokens["refresh_token"] is not None
    }


@router.post("/tokens/refresh")
async def refresh_token(
    yahoo: YahooFantasyService = Depends(get_yahoo_service)
) -> Dict[str, str]:
    """Manually refresh access token"""
    try:
        token_data = await yahoo.refresh_access_token()
        
        return {
            "status": "success",
            "message": "Token refreshed successfully",
            "expires_in": str(token_data.get("expires_in", 0)) + " seconds"
        }
    except YahooOAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
