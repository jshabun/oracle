"""
Player Analytics Engine
Handles 9-category player evaluation and ranking
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class PlayerStats:
    """Player statistics for a season"""
    player_id: str
    name: str
    position: List[str]
    team: str
    games_played: int
    
    # Counting stats (per game averages)
    fg_made: float
    fg_attempted: float
    ft_made: float
    ft_attempted: float
    three_pm: float
    points: float
    rebounds: float
    assists: float
    steals: float
    blocks: float
    turnovers: float
    
    @property
    def fg_pct(self) -> Optional[float]:
        """Calculate FG%"""
        if self.fg_attempted == 0:
            return None
        return self.fg_made / self.fg_attempted
    
    @property
    def ft_pct(self) -> Optional[float]:
        """Calculate FT%"""
        if self.ft_attempted == 0:
            return None
        return self.ft_made / self.ft_attempted


class CategoryAnalyzer:
    """Analyzes players across 9 categories using Z-scores"""
    
    def __init__(self):
        self.categories = settings.CATEGORIES
        self.negative_cats = settings.NEGATIVE_CATEGORIES
        self.percentage_cats = settings.PERCENTAGE_CATEGORIES
        
    def calculate_z_scores(
        self, 
        players: List[PlayerStats],
        min_games: int = 20
    ) -> pd.DataFrame:
        """
        Calculate Z-scores for all categories
        
        For percentage stats (FG%, FT%), we need to weight by volume
        to properly calculate league averages.
        """
        # Filter players by minimum games
        filtered_players = [p for p in players if p.games_played >= min_games]
        
        if not filtered_players:
            return pd.DataFrame()
        
        # Create DataFrame
        data = []
        for player in filtered_players:
            row = {
                'player_id': player.player_id,
                'name': player.name,
                'position': ','.join(player.position),
                'team': player.team,
                'games_played': player.games_played,
                'FG%': player.fg_pct,
                'FT%': player.ft_pct,
                '3PM': player.three_pm,
                'PTS': player.points,
                'REB': player.rebounds,
                'AST': player.assists,
                'STL': player.steals,
                'BLK': player.blocks,
                'TO': player.turnovers,
                'fg_made': player.fg_made,
                'fg_attempted': player.fg_attempted,
                'ft_made': player.ft_made,
                'ft_attempted': player.ft_attempted,
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Calculate Z-scores for each category
        z_scores = pd.DataFrame()
        z_scores['player_id'] = df['player_id']
        z_scores['name'] = df['name']
        z_scores['position'] = df['position']
        
        for cat in self.categories:
            if cat in self.percentage_cats:
                # For percentage stats, calculate league average weighted by attempts
                if cat == 'FG%':
                    total_made = (df['fg_made'] * df['games_played']).sum()
                    total_attempted = (df['fg_attempted'] * df['games_played']).sum()
                    league_avg = total_made / total_attempted if total_attempted > 0 else 0
                    
                    # Calculate contribution to team FG%
                    # Player's impact is their deviation from league average, weighted by volume
                    df[f'{cat}_impact'] = (df['FG%'] - league_avg) * df['fg_attempted']
                    values = df[f'{cat}_impact']
                    
                elif cat == 'FT%':
                    total_made = (df['ft_made'] * df['games_played']).sum()
                    total_attempted = (df['ft_attempted'] * df['games_played']).sum()
                    league_avg = total_made / total_attempted if total_attempted > 0 else 0
                    
                    df[f'{cat}_impact'] = (df['FT%'] - league_avg) * df['ft_attempted']
                    values = df[f'{cat}_impact']
            else:
                values = df[cat]
            
            # Calculate mean and std
            mean = values.mean()
            std = values.std()
            
            # Calculate Z-score
            if std > 0:
                z_scores[f'{cat}_z'] = (values - mean) / std
            else:
                z_scores[f'{cat}_z'] = 0
            
            # Flip sign for negative categories (TO)
            if cat in self.negative_cats:
                z_scores[f'{cat}_z'] = -z_scores[f'{cat}_z']
        
        # Calculate total Z-score (sum of all categories)
        z_cols = [col for col in z_scores.columns if col.endswith('_z')]
        z_scores['total_z'] = z_scores[z_cols].sum(axis=1)
        
        # Rank by total Z-score
        z_scores['rank'] = z_scores['total_z'].rank(ascending=False)
        
        return z_scores.sort_values('rank')
    
    def identify_punt_categories(
        self,
        current_team: List[PlayerStats]
    ) -> List[str]:
        """
        Identify which categories the current team is weak in
        This helps inform punt strategy decisions
        """
        if not current_team:
            return []
        
        # Calculate team's Z-scores
        team_z = self.calculate_z_scores(current_team, min_games=0)
        
        # Find categories with negative Z-scores
        weak_cats = []
        for cat in self.categories:
            z_col = f'{cat}_z'
            if z_col in team_z.columns:
                avg_z = team_z[z_col].mean()
                if avg_z < -0.5:  # Threshold for "weak"
                    weak_cats.append(cat)
        
        return weak_cats
    
    def calculate_marginal_value(
        self,
        player: PlayerStats,
        all_players: List[PlayerStats],
        replacement_level: int = 100
    ) -> float:
        """
        Calculate player's value above replacement level
        Replacement level = Xth best available player
        """
        z_scores = self.calculate_z_scores(all_players)
        
        if replacement_level >= len(z_scores):
            replacement_level = len(z_scores) - 1
        
        replacement_z = z_scores.iloc[replacement_level]['total_z']
        
        player_row = z_scores[z_scores['player_id'] == player.player_id]
        if player_row.empty:
            return 0.0
        
        player_z = player_row['total_z'].values[0]
        
        return player_z - replacement_z


class DraftEngine:
    """Handles draft logic and recommendations"""
    
    def __init__(self, analyzer: CategoryAnalyzer):
        self.analyzer = analyzer
        self.league_size = settings.LEAGUE_SIZE
        
    def get_draft_recommendations(
        self,
        available_players: List[PlayerStats],
        current_roster: List[PlayerStats],
        draft_position: int,
        current_pick: int,
        snake: bool = True
    ) -> List[Tuple[PlayerStats, float, Dict[str, float]]]:
        """
        Get top draft recommendations
        
        Returns list of (player, value, category_z_scores)
        """
        # Calculate Z-scores for available players
        z_scores = self.analyzer.calculate_z_scores(available_players)
        
        if z_scores.empty:
            return []
        
        # Identify positional needs
        roster_positions = self._get_roster_positions(current_roster)
        
        # Identify punt categories (if any emerging)
        punt_cats = self.analyzer.identify_punt_categories(current_roster)
        
        # Adjust rankings based on team needs
        recommendations = []
        for _, row in z_scores.head(20).iterrows():
            player = next((p for p in available_players if p.player_id == row['player_id']), None)
            if not player:
                continue
            
            # Base value is total Z-score
            value = row['total_z']
            
            # Boost value if fills positional need
            # (This is simplified - could be more sophisticated)
            
            # Category Z-scores
            cat_z = {cat: row[f'{cat}_z'] for cat in settings.CATEGORIES}
            
            recommendations.append((player, value, cat_z))
        
        return sorted(recommendations, key=lambda x: x[1], reverse=True)
    
    def _get_roster_positions(self, roster: List[PlayerStats]) -> Dict[str, int]:
        """Count positions on current roster"""
        positions = {pos: 0 for pos in ['PG', 'SG', 'SF', 'PF', 'C']}
        for player in roster:
            for pos in player.position:
                if pos in positions:
                    positions[pos] += 1
        return positions
