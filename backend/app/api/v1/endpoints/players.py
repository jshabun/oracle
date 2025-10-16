"""
Players endpoints - player stats, rankings, projections
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional, Dict, Any

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


@router.get("/search")
async def search_players(
    league_key: str = Query(..., description="League key (e.g., nba.l.12345)"),
    query: str = Query(..., description="Player name to search"),
    limit: int = Query(20, description="Maximum results"),
    player_service: PlayerDataService = Depends(get_player_service)
) -> Dict[str, Any]:
    """
    Search for players by name with stats and rankings
    
    Returns players with:
    - Basic info (name, team, position)
    - Season statistics
    - Z-scores across all categories
    - Overall ranking
    """
    try:
        results = await player_service.search_players(
            league_key=league_key,
            query=query,
            limit=limit
        )
        
        return {
            "query": query,
            "players": results,
            "count": len(results)
        }
        
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching players: {str(e)}")


@router.get("/rankings")
async def get_player_rankings(
    league_key: str = Query(..., description="League key"),
    limit: int = Query(50, description="Number of players to return"),
    player_service: PlayerDataService = Depends(get_player_service)
) -> Dict[str, Any]:
    """
    Get overall player rankings based on total Z-score
    
    Returns top players ranked by their total fantasy value across all 9 categories
    """
    try:
        rankings = await player_service.get_player_rankings(
            league_key=league_key,
            category=None,
            limit=limit
        )
        
        return {
            "rankings": rankings,
            "count": len(rankings),
            "scoring_system": "9-category Z-score"
        }
        
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rankings: {str(e)}")


@router.get("/rankings/category/{category}")
async def get_category_rankings(
    category: str,
    league_key: str = Query(..., description="League key"),
    limit: int = Query(50, description="Number of players to return"),
    player_service: PlayerDataService = Depends(get_player_service)
) -> Dict[str, Any]:
    """
    Get player rankings by specific category
    
    Valid categories: FG%, FT%, 3PM, PTS, REB, AST, STL, BLK, TO
    """
    valid_categories = ["FG%", "FT%", "3PM", "PTS", "REB", "AST", "STL", "BLK", "TO"]
    
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    try:
        rankings = await player_service.get_player_rankings(
            league_key=league_key,
            category=category,
            limit=limit
        )
        
        return {
            "category": category,
            "rankings": rankings,
            "count": len(rankings)
        }
        
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rankings: {str(e)}")


@router.get("/available")
async def get_available_players_analyzed(
    league_key: str = Query(..., description="League key"),
    position: Optional[str] = Query(None, description="Filter by position"),
    limit: int = Query(100, description="Maximum players"),
    player_service: PlayerDataService = Depends(get_player_service)
) -> Dict[str, Any]:
    """
    Get available (free agent) players with full statistical analysis
    
    Returns players with:
    - Complete stats across all 9 categories
    - Z-scores showing value in each category
    - Overall fantasy ranking
    """
    try:
        players = await player_service.get_available_players_with_stats(
            league_key=league_key,
            position=position,
            limit=limit
        )
        
        # Calculate Z-scores for all players
        from app.core.analytics import CategoryAnalyzer
        analyzer = CategoryAnalyzer()
        z_scores_df = analyzer.calculate_z_scores(players)
        
        # Format response
        results = []
        for player in players:
            player_row = z_scores_df[z_scores_df["player_id"] == player.player_id]
            
            if not player_row.empty:
                cat_z = {
                    cat: player_row.iloc[0][f"{cat}_z"]
                    for cat in settings.CATEGORIES
                    if f"{cat}_z" in player_row.columns
                }
                cat_z["total_z"] = player_row.iloc[0].get("total_z", 0)
                
                from app.services.data_mapper import YahooDataMapper
                mapper = YahooDataMapper()
                results.append(mapper.format_player_for_response(player, z_scores=cat_z))
        
        # Sort by total value
        results.sort(key=lambda x: x.get("total_value", 0), reverse=True)
        
        return {
            "league_key": league_key,
            "position_filter": position,
            "players": results,
            "count": len(results)
        }
        
    except YahooOAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except YahooAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching players: {str(e)}")
