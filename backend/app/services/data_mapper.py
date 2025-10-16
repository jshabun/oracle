"""
Player Data Mapper
Converts Yahoo Fantasy API data to our PlayerStats model
"""
from typing import Dict, Any, Optional, List
from app.core.analytics import PlayerStats


class YahooDataMapper:
    """Maps Yahoo Fantasy API data to our internal data models"""
    
    # Yahoo stat IDs to our category names
    # These IDs are from Yahoo's API response
    STAT_ID_MAP = {
        "FG%": "5",      # Field Goal Percentage
        "FT%": "15",     # Free Throw Percentage  
        "3PM": "10",     # 3-Point Field Goals Made
        "PTS": "12",     # Points
        "REB": "18",     # Total Rebounds
        "AST": "13",     # Assists
        "STL": "16",     # Steals
        "BLK": "17",     # Blocks
        "TO": "11",      # Turnovers
        
        # Additional stats we need for calculations
        "FGM": "9",      # Field Goals Made
        "FGA": "8",      # Field Goals Attempted
        "FTM": "14",     # Free Throws Made
        "FTA": "13",     # Free Throws Attempted
        "GP": "0",       # Games Played
    }
    
    @staticmethod
    def parse_player_stats(player_data: Dict[str, Any]) -> Optional[PlayerStats]:
        """
        Parse Yahoo player data into PlayerStats object
        
        Args:
            player_data: Raw player data from Yahoo API
            
        Returns:
            PlayerStats object or None if data is invalid
        """
        try:
            # Extract basic player info
            player_id = str(player_data.get("player_id", ""))
            name = player_data.get("name", {}).get("full", "Unknown")
            
            # Get positions (Yahoo returns list like [{"position": "PG"}, {"position": "SG"}])
            positions_data = player_data.get("eligible_positions", [])
            if isinstance(positions_data, list):
                if positions_data and isinstance(positions_data[0], dict):
                    positions = [pos.get("position") for pos in positions_data if "position" in pos]
                else:
                    positions = positions_data
            else:
                positions = []
            
            # Filter out utility positions
            positions = [p for p in positions if p in ["PG", "SG", "SF", "PF", "C", "G", "F"]]
            if not positions:
                positions = ["UTIL"]
            
            team = player_data.get("editorial_team_abbr", "FA")
            
            # Extract stats
            # Yahoo returns stats in various formats depending on the endpoint
            stats_data = None
            
            # Try to find stats in common locations
            if "player_stats" in player_data:
                stats_data = player_data["player_stats"]
            elif "stats" in player_data:
                stats_data = player_data["stats"]
            elif len(player_data) > 1 and isinstance(player_data[1], dict):
                # Sometimes stats are in index [1]
                if "player_stats" in player_data[1]:
                    stats_data = player_data[1]["player_stats"]
                elif "stats" in player_data[1]:
                    stats_data = player_data[1]["stats"]
            
            if not stats_data:
                # No stats available, return basic player info with zeros
                return PlayerStats(
                    player_id=player_id,
                    name=name,
                    position=positions,
                    team=team,
                    games_played=0,
                    fg_made=0.0,
                    fg_attempted=0.0,
                    ft_made=0.0,
                    ft_attempted=0.0,
                    three_pm=0.0,
                    points=0.0,
                    rebounds=0.0,
                    assists=0.0,
                    steals=0.0,
                    blocks=0.0,
                    turnovers=0.0
                )
            
            # Parse stats - Yahoo returns array of {stat_id: value}
            stat_dict = YahooDataMapper._parse_stat_array(stats_data)
            
            # Extract individual stats
            games_played = int(stat_dict.get("GP", 0))
            if games_played == 0:
                games_played = 1  # Avoid division by zero
            
            return PlayerStats(
                player_id=player_id,
                name=name,
                position=positions,
                team=team,
                games_played=games_played,
                fg_made=float(stat_dict.get("FGM", 0)) / games_played,
                fg_attempted=float(stat_dict.get("FGA", 0)) / games_played,
                ft_made=float(stat_dict.get("FTM", 0)) / games_played,
                ft_attempted=float(stat_dict.get("FTA", 0)) / games_played,
                three_pm=float(stat_dict.get("3PM", 0)) / games_played,
                points=float(stat_dict.get("PTS", 0)) / games_played,
                rebounds=float(stat_dict.get("REB", 0)) / games_played,
                assists=float(stat_dict.get("AST", 0)) / games_played,
                steals=float(stat_dict.get("STL", 0)) / games_played,
                blocks=float(stat_dict.get("BLK", 0)) / games_played,
                turnovers=float(stat_dict.get("TO", 0)) / games_played
            )
            
        except Exception as e:
            print(f"Error parsing player {player_data.get('name', 'unknown')}: {e}")
            return None
    
    @staticmethod
    def _parse_stat_array(stats_data: Any) -> Dict[str, float]:
        """
        Parse Yahoo's stat array format into a dictionary
        
        Yahoo returns stats in various formats:
        1. {"stats": [{"stat": {"stat_id": "0", "value": "10"}}, ...]}
        2. {"stat": [{"stat_id": "0", "value": "10"}, ...]}
        3. [{"stat_id": "0", "value": "10"}, ...]
        """
        stat_dict = {}
        
        # Find the stat array
        stat_array = None
        if isinstance(stats_data, dict):
            if "stats" in stats_data:
                stat_array = stats_data["stats"]
            elif "stat" in stats_data:
                stat_array = stats_data["stat"]
        elif isinstance(stats_data, list):
            stat_array = stats_data
        
        if not stat_array:
            return stat_dict
        
        # Reverse map: stat_id -> category name
        id_to_name = {v: k for k, v in YahooDataMapper.STAT_ID_MAP.items()}
        
        # Parse each stat
        for item in stat_array:
            if isinstance(item, dict):
                # Handle nested format {"stat": {"stat_id": "0", "value": "10"}}
                stat = item.get("stat", item)
                
                stat_id = str(stat.get("stat_id", ""))
                value = stat.get("value", "0")
                
                # Convert to category name
                if stat_id in id_to_name:
                    category = id_to_name[stat_id]
                    try:
                        stat_dict[category] = float(value) if value else 0.0
                    except (ValueError, TypeError):
                        stat_dict[category] = 0.0
        
        return stat_dict
    
    @staticmethod
    def parse_multiple_players(players_data: List[Dict[str, Any]]) -> List[PlayerStats]:
        """
        Parse a list of Yahoo players into PlayerStats objects
        
        Args:
            players_data: List of raw player data from Yahoo API
            
        Returns:
            List of PlayerStats objects (excluding invalid entries)
        """
        player_stats = []
        
        for player_data in players_data:
            player_stat = YahooDataMapper.parse_player_stats(player_data)
            if player_stat:
                player_stats.append(player_stat)
        
        return player_stats
    
    @staticmethod
    def extract_player_key(player_data: Dict[str, Any]) -> Optional[str]:
        """Extract player_key from Yahoo player data"""
        return player_data.get("player_key")
    
    @staticmethod
    def format_player_for_response(
        player_stat: PlayerStats,
        z_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Format PlayerStats object for API response
        
        Args:
            player_stat: PlayerStats object
            z_scores: Optional Z-scores for categories
            
        Returns:
            Dictionary suitable for JSON response
        """
        response = {
            "player_id": player_stat.player_id,
            "name": player_stat.name,
            "position": player_stat.position,
            "team": player_stat.team,
            "games_played": player_stat.games_played,
            "stats": {
                "FG%": round(player_stat.fg_pct * 100, 1) if player_stat.fg_pct else 0,
                "FT%": round(player_stat.ft_pct * 100, 1) if player_stat.ft_pct else 0,
                "3PM": round(player_stat.three_pm, 1),
                "PTS": round(player_stat.points, 1),
                "REB": round(player_stat.rebounds, 1),
                "AST": round(player_stat.assists, 1),
                "STL": round(player_stat.steals, 1),
                "BLK": round(player_stat.blocks, 1),
                "TO": round(player_stat.turnovers, 1),
            }
        }
        
        if z_scores:
            response["z_scores"] = {
                k: round(v, 2) for k, v in z_scores.items()
            }
            
            # Add total Z-score if available
            if "total_z" in z_scores:
                response["total_value"] = round(z_scores["total_z"], 2)
        
        return response
