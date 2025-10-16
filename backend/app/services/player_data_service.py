"""
Player Data Service
Fetches and integrates player data from Yahoo with analytics
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

from app.services.yahoo_fantasy import YahooFantasyService, YahooAPIError
from app.services.data_mapper import YahooDataMapper
from app.core.analytics import PlayerStats, CategoryAnalyzer, DraftEngine


class PlayerDataService:
    """
    Service for fetching and analyzing player data
    Bridges Yahoo API and Analytics Engine
    """
    
    def __init__(self, yahoo_service: YahooFantasyService):
        self.yahoo = yahoo_service
        self.mapper = YahooDataMapper()
        self.analyzer = CategoryAnalyzer()
        self.draft_engine = DraftEngine(self.analyzer)
        
        # Simple in-memory cache
        self._player_cache: Dict[str, PlayerStats] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(hours=6)  # Cache for 6 hours
    
    async def get_available_players_with_stats(
        self,
        league_key: str,
        position: Optional[str] = None,
        limit: int = 100
    ) -> List[PlayerStats]:
        """
        Get available players with their statistics
        
        Args:
            league_key: Yahoo league key
            position: Optional position filter
            limit: Maximum players to fetch
            
        Returns:
            List of PlayerStats objects with statistics
        """
        # Fetch available players from Yahoo
        yahoo_players = await self.yahoo.get_available_players(
            league_key=league_key,
            position=position,
            count=limit
        )
        
        # Fetch stats for each player
        player_stats_list = []
        
        # Process in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(yahoo_players), batch_size):
            batch = yahoo_players[i:i+batch_size]
            
            # Fetch stats for each player in batch
            tasks = []
            for player in batch:
                player_key = self.mapper.extract_player_key(player)
                if player_key:
                    tasks.append(self._fetch_player_with_stats(player, player_key))
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Add successful results
            for result in batch_results:
                if isinstance(result, PlayerStats):
                    player_stats_list.append(result)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(yahoo_players):
                await asyncio.sleep(0.5)
        
        return player_stats_list
    
    async def _fetch_player_with_stats(
        self,
        player_data: Dict[str, Any],
        player_key: str
    ) -> Optional[PlayerStats]:
        """Fetch a single player with stats"""
        try:
            # Get player stats from Yahoo
            stats_data = await self.yahoo.get_player_stats(
                player_key=player_key,
                stat_type="season"
            )
            
            # Merge basic info with stats
            player_with_stats = {**player_data}
            if "player_stats" in stats_data:
                player_with_stats["player_stats"] = stats_data["player_stats"]
            elif "stats" in stats_data:
                player_with_stats["stats"] = stats_data["stats"]
            
            # Parse into PlayerStats
            return self.mapper.parse_player_stats(player_with_stats)
            
        except Exception as e:
            print(f"Error fetching stats for {player_data.get('name', 'unknown')}: {e}")
            return None
    
    async def get_draft_recommendations(
        self,
        league_key: str,
        current_roster: List[str],
        draft_position: int,
        current_pick: int,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get draft recommendations using real Yahoo data
        
        Args:
            league_key: Yahoo league key
            current_roster: List of player_ids already drafted
            draft_position: Your draft position (1-10)
            current_pick: Current overall pick number
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended players with rankings
        """
        # Get available players with stats
        available_players = await self.get_available_players_with_stats(
            league_key=league_key,
            limit=200  # Get top 200 for better analysis
        )
        
        # Filter out already drafted players
        available_players = [
            p for p in available_players
            if p.player_id not in current_roster
        ]
        
        if not available_players:
            return []
        
        # Get current roster as PlayerStats objects
        roster_stats = [
            p for p in available_players
            if p.player_id in current_roster
        ]
        
        # Use draft engine to get recommendations
        recommendations = self.draft_engine.get_draft_recommendations(
            available_players=available_players,
            current_roster=roster_stats,
            draft_position=draft_position,
            current_pick=current_pick,
            snake=True
        )
        
        # Format for response
        formatted_recs = []
        for player, value, cat_z in recommendations[:top_n]:
            formatted_recs.append({
                "player": self.mapper.format_player_for_response(
                    player,
                    z_scores=cat_z
                ),
                "draft_value": round(value, 2),
                "rank": len(formatted_recs) + 1,
                "category_fit": self._analyze_category_fit(cat_z, roster_stats)
            })
        
        return formatted_recs
    
    def _analyze_category_fit(
        self,
        player_z: Dict[str, float],
        current_roster: List[PlayerStats]
    ) -> Dict[str, str]:
        """
        Analyze how player fits team's category needs
        
        Returns:
            Dictionary of categories and their fit level
        """
        if not current_roster:
            return {"overall": "balanced"}
        
        # Calculate current team's category strengths
        team_z = self.analyzer.calculate_z_scores(current_roster)
        
        fit = {}
        for cat in ["FG%", "FT%", "3PM", "PTS", "REB", "AST", "STL", "BLK", "TO"]:
            z_col = f"{cat}_z"
            
            if z_col in player_z:
                player_value = player_z[z_col]
                
                # Determine fit
                if player_value > 1.5:
                    fit[cat] = "excellent"
                elif player_value > 0.5:
                    fit[cat] = "good"
                elif player_value > -0.5:
                    fit[cat] = "neutral"
                else:
                    fit[cat] = "weak"
        
        return fit
    
    async def get_player_rankings(
        self,
        league_key: str,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get player rankings overall or by category
        
        Args:
            league_key: Yahoo league key
            category: Optional category to rank by
            limit: Number of players to return
            
        Returns:
            List of ranked players
        """
        # Get available players with stats
        players = await self.get_available_players_with_stats(
            league_key=league_key,
            limit=200
        )
        
        if not players:
            return []
        
        # Calculate Z-scores
        z_scores_df = self.analyzer.calculate_z_scores(players)
        
        # Sort by category or total
        if category and f"{category}_z" in z_scores_df.columns:
            z_scores_df = z_scores_df.sort_values(f"{category}_z", ascending=False)
        else:
            z_scores_df = z_scores_df.sort_values("total_z", ascending=False)
        
        # Format response
        rankings = []
        for idx, row in z_scores_df.head(limit).iterrows():
            player = next(
                (p for p in players if p.player_id == row["player_id"]),
                None
            )
            
            if player:
                # Extract Z-scores
                cat_z = {
                    cat: row[f"{cat}_z"]
                    for cat in ["FG%", "FT%", "3PM", "PTS", "REB", "AST", "STL", "BLK", "TO"]
                    if f"{cat}_z" in row
                }
                cat_z["total_z"] = row.get("total_z", 0)
                
                rankings.append(
                    self.mapper.format_player_for_response(player, z_scores=cat_z)
                )
        
        return rankings
    
    async def search_players(
        self,
        league_key: str,
        query: str,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Search for players and return with stats/rankings
        
        Args:
            league_key: Yahoo league key
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching players with stats
        """
        # Search via Yahoo API
        yahoo_players = await self.yahoo.search_players(
            league_key=league_key,
            search_term=query,
            count=limit
        )
        
        # Fetch stats for each player
        player_stats_list = []
        for player in yahoo_players:
            player_key = self.mapper.extract_player_key(player)
            if player_key:
                player_stat = await self._fetch_player_with_stats(player, player_key)
                if player_stat:
                    player_stats_list.append(player_stat)
        
        # Calculate Z-scores if we have enough players
        if len(player_stats_list) >= 10:
            z_scores_df = self.analyzer.calculate_z_scores(player_stats_list)
            
            # Format with Z-scores
            results = []
            for player in player_stats_list:
                player_row = z_scores_df[z_scores_df["player_id"] == player.player_id]
                
                if not player_row.empty:
                    cat_z = {
                        cat: player_row.iloc[0][f"{cat}_z"]
                        for cat in ["FG%", "FT%", "3PM", "PTS", "REB", "AST", "STL", "BLK", "TO"]
                        if f"{cat}_z" in player_row.columns
                    }
                    cat_z["total_z"] = player_row.iloc[0].get("total_z", 0)
                    
                    results.append(
                        self.mapper.format_player_for_response(player, z_scores=cat_z)
                    )
                else:
                    results.append(self.mapper.format_player_for_response(player))
            
            return results
        else:
            # Not enough players for Z-score calculation, return basic info
            return [
                self.mapper.format_player_for_response(player)
                for player in player_stats_list
            ]
    
    async def analyze_trade(
        self,
        league_key: str,
        give_player_ids: List[str],
        receive_player_ids: List[str],
        current_roster_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze a trade proposal
        
        Args:
            league_key: Yahoo league key
            give_player_ids: Players you're giving up
            receive_player_ids: Players you're receiving
            current_roster_ids: Your current roster
            
        Returns:
            Trade analysis with recommendations
        """
        # Get all relevant players
        all_ids = set(give_player_ids + receive_player_ids + current_roster_ids)
        
        # Fetch player stats (simplified - in production you'd batch this)
        all_players = []
        for player_id in all_ids:
            # Search for player (this is simplified)
            results = await self.search_players(league_key, player_id, limit=1)
            if results:
                # Convert back to PlayerStats
                # This is a simplification - in production you'd have better player lookup
                pass
        
        # For now, return placeholder
        return {
            "recommendation": "analyze",
            "net_value_change": 0.0,
            "category_impact": {},
            "note": "Trade analysis coming soon - needs player lookup implementation"
        }
