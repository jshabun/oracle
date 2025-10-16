"""
Yahoo Fantasy API Service
Handles OAuth authentication and API requests
"""
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from app.core.config import settings


class YahooOAuthError(Exception):
    """Yahoo OAuth related errors"""
    pass


class YahooAPIError(Exception):
    """Yahoo API request errors"""
    pass


class YahooFantasyService:
    """
    Service for interacting with Yahoo Fantasy Sports API
    
    OAuth 2.0 Flow:
    1. Get authorization URL
    2. User logs in and authorizes
    3. Yahoo redirects with code
    4. Exchange code for access token
    5. Use access token for API requests
    6. Refresh token when expired
    """
    
    BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"
    AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
    TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
    
    def __init__(
        self,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None
    ):
        self.consumer_key = consumer_key or settings.YAHOO_CONSUMER_KEY
        self.consumer_secret = consumer_secret or settings.YAHOO_CONSUMER_SECRET
        
        if not self.consumer_key or not self.consumer_secret:
            raise YahooOAuthError(
                "Yahoo API credentials not configured. "
                "Set YAHOO_CONSUMER_KEY and YAHOO_CONSUMER_SECRET in .env"
            )
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Get Yahoo OAuth authorization URL
        
        Args:
            redirect_uri: Where Yahoo should redirect after authorization
            
        Returns:
            Authorization URL for user to visit
        """
        params = {
            "client_id": self.consumer_key,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "language": "en-us"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from Yahoo redirect
            redirect_uri: Must match the redirect_uri used in authorization
            
        Returns:
            Token data including access_token, refresh_token, expires_in
        """
        data = {
            "client_id": self.consumer_key,
            "client_secret": self.consumer_secret,
            "redirect_uri": redirect_uri,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise YahooOAuthError(
                    f"Token exchange failed: {response.status_code} - {response.text}"
                )
            
            token_data = response.json()
            
            # Store tokens
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expires_at = datetime.now() + timedelta(
                seconds=token_data["expires_in"]
            )
            
            return token_data
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Returns:
            New token data
        """
        if not self.refresh_token:
            raise YahooOAuthError("No refresh token available")
        
        data = {
            "client_id": self.consumer_key,
            "client_secret": self.consumer_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise YahooOAuthError(
                    f"Token refresh failed: {response.status_code} - {response.text}"
                )
            
            token_data = response.json()
            
            # Update tokens
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expires_at = datetime.now() + timedelta(
                seconds=token_data["expires_in"]
            )
            
            return token_data
    
    async def _ensure_valid_token(self):
        """Ensure we have a valid access token, refresh if needed"""
        if not self.access_token:
            raise YahooOAuthError("Not authenticated. Please authorize first.")
        
        # Refresh if token expires in less than 5 minutes
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            await self.refresh_access_token()
    
    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Yahoo Fantasy API
        
        Args:
            endpoint: API endpoint (e.g., "/league/nba.l.12345")
            params: Query parameters
            
        Returns:
            API response data
        """
        await self._ensure_valid_token()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        # Add format parameter for JSON response
        if params is None:
            params = {}
        params["format"] = "json"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            
            if response.status_code == 401:
                # Token might be expired, try refreshing
                await self.refresh_access_token()
                response = await client.get(url, params=params, headers=headers)
            
            if response.status_code != 200:
                raise YahooAPIError(
                    f"API request failed: {response.status_code} - {response.text}"
                )
            
            return response.json()
    
    # === League API Methods ===
    
    async def get_user_leagues(self, sport: str = "nba", season: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all leagues for authenticated user
        
        Args:
            sport: Sport type (nba, nfl, mlb, nhl)
            season: Season year (e.g., 2024)
            
        Returns:
            List of league data
        """
        if season is None:
            season = datetime.now().year
        
        endpoint = f"/users;use_login=1/games;game_keys={sport}/leagues"
        data = await self._make_request(endpoint)
        
        # Parse Yahoo's complex response structure
        try:
            games = data["fantasy_content"]["users"]["0"]["user"][1]["games"]
            leagues = []
            
            for key, value in games.items():
                if key == "count":
                    continue
                if isinstance(value, dict) and "game" in value:
                    game_leagues = value["game"][1].get("leagues", {})
                    for league_key, league_data in game_leagues.items():
                        if league_key == "count":
                            continue
                        if isinstance(league_data, dict) and "league" in league_data:
                            leagues.append(league_data["league"][0])
            
            return leagues
        except (KeyError, IndexError, TypeError) as e:
            raise YahooAPIError(f"Failed to parse leagues response: {e}")
    
    async def get_league_settings(self, league_key: str) -> Dict[str, Any]:
        """
        Get league settings and configuration
        
        Args:
            league_key: League key (e.g., "nba.l.12345")
            
        Returns:
            League settings data
        """
        endpoint = f"/league/{league_key}/settings"
        data = await self._make_request(endpoint)
        
        try:
            return data["fantasy_content"]["league"][1]["settings"][0]
        except (KeyError, IndexError) as e:
            raise YahooAPIError(f"Failed to parse league settings: {e}")
    
    async def get_league_standings(self, league_key: str) -> List[Dict[str, Any]]:
        """
        Get league standings
        
        Args:
            league_key: League key
            
        Returns:
            List of team standings
        """
        endpoint = f"/league/{league_key}/standings"
        data = await self._make_request(endpoint)
        
        try:
            standings_data = data["fantasy_content"]["league"][1]["standings"][0]["teams"]
            teams = []
            
            for key, value in standings_data.items():
                if key == "count":
                    continue
                if isinstance(value, dict) and "team" in value:
                    teams.append(value["team"][0])
            
            return teams
        except (KeyError, IndexError) as e:
            raise YahooAPIError(f"Failed to parse standings: {e}")
    
    # === Team API Methods ===
    
    async def get_team_roster(self, team_key: str) -> List[Dict[str, Any]]:
        """
        Get team roster
        
        Args:
            team_key: Team key (e.g., "nba.l.12345.t.1")
            
        Returns:
            List of players on roster
        """
        endpoint = f"/team/{team_key}/roster"
        data = await self._make_request(endpoint)
        
        try:
            roster_data = data["fantasy_content"]["team"][1]["roster"]["0"]["players"]
            players = []
            
            for key, value in roster_data.items():
                if key == "count":
                    continue
                if isinstance(value, dict) and "player" in value:
                    players.append(value["player"][0])
            
            return players
        except (KeyError, IndexError) as e:
            raise YahooAPIError(f"Failed to parse roster: {e}")
    
    async def get_team_matchup(self, team_key: str, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Get team's matchup for a specific week
        
        Args:
            team_key: Team key
            week: Week number (current week if not specified)
            
        Returns:
            Matchup data
        """
        if week:
            endpoint = f"/team/{team_key}/matchups;weeks={week}"
        else:
            endpoint = f"/team/{team_key}/matchups"
        
        data = await self._make_request(endpoint)
        
        try:
            return data["fantasy_content"]["team"][1]["matchups"]
        except (KeyError, IndexError) as e:
            raise YahooAPIError(f"Failed to parse matchup: {e}")
    
    # === Player API Methods ===
    
    async def get_available_players(
        self,
        league_key: str,
        position: Optional[str] = None,
        status: str = "A",  # A = Available, FA = Free Agent
        start: int = 0,
        count: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Get available players in league
        
        Args:
            league_key: League key
            position: Filter by position (PG, SG, SF, PF, C, G, F, UTIL)
            status: Player status (A = Available)
            start: Starting index for pagination
            count: Number of players to return
            
        Returns:
            List of available players
        """
        endpoint = f"/league/{league_key}/players;status={status}"
        
        if position:
            endpoint += f";position={position}"
        
        endpoint += f";start={start};count={count}"
        
        data = await self._make_request(endpoint)
        
        try:
            players_data = data["fantasy_content"]["league"][1]["players"]
            players = []
            
            for key, value in players_data.items():
                if key == "count":
                    continue
                if isinstance(value, dict) and "player" in value:
                    players.append(value["player"][0])
            
            return players
        except (KeyError, IndexError) as e:
            raise YahooAPIError(f"Failed to parse available players: {e}")
    
    async def get_player_stats(
        self,
        player_key: str,
        stat_type: str = "season"  # season, average_season, week, etc.
    ) -> Dict[str, Any]:
        """
        Get player statistics
        
        Args:
            player_key: Player key (e.g., "nba.p.5479")
            stat_type: Type of stats to retrieve
            
        Returns:
            Player stats data
        """
        endpoint = f"/player/{player_key}/stats;type={stat_type}"
        data = await self._make_request(endpoint)
        
        try:
            return data["fantasy_content"]["player"][1]
        except (KeyError, IndexError) as e:
            raise YahooAPIError(f"Failed to parse player stats: {e}")
    
    async def search_players(
        self,
        league_key: str,
        search_term: str,
        start: int = 0,
        count: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Search for players by name
        
        Args:
            league_key: League key
            search_term: Player name to search
            start: Starting index
            count: Number of results
            
        Returns:
            List of matching players
        """
        endpoint = f"/league/{league_key}/players;search={search_term};start={start};count={count}"
        data = await self._make_request(endpoint)
        
        try:
            players_data = data["fantasy_content"]["league"][1]["players"]
            players = []
            
            for key, value in players_data.items():
                if key == "count":
                    continue
                if isinstance(value, dict) and "player" in value:
                    players.append(value["player"][0])
            
            return players
        except (KeyError, IndexError) as e:
            raise YahooAPIError(f"Failed to parse search results: {e}")
    
    # === Transaction API Methods ===
    
    async def get_league_transactions(
        self,
        league_key: str,
        transaction_type: Optional[str] = None  # add, drop, trade, etc.
    ) -> List[Dict[str, Any]]:
        """
        Get league transactions
        
        Args:
            league_key: League key
            transaction_type: Filter by transaction type
            
        Returns:
            List of transactions
        """
        endpoint = f"/league/{league_key}/transactions"
        
        if transaction_type:
            endpoint += f";type={transaction_type}"
        
        data = await self._make_request(endpoint)
        
        try:
            transactions_data = data["fantasy_content"]["league"][1]["transactions"]
            transactions = []
            
            for key, value in transactions_data.items():
                if key == "count":
                    continue
                if isinstance(value, dict) and "transaction" in value:
                    transactions.append(value["transaction"][0])
            
            return transactions
        except (KeyError, IndexError) as e:
            raise YahooAPIError(f"Failed to parse transactions: {e}")
    
    # === Token Management ===
    
    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        expires_in: int
    ):
        """Set tokens manually (e.g., from database)"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
    
    def get_tokens(self) -> Dict[str, Any]:
        """Get current tokens for storage"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        }
