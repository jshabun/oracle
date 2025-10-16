# API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints require Yahoo OAuth authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Yahoo Fantasy Integration

### GET `/yahoo/auth/url`
Get Yahoo OAuth authorization URL

**Response:**
```json
{
  "auth_url": "https://api.login.yahoo.com/oauth2/request_auth?...",
  "status": "success"
}
```

### GET `/yahoo/league/info`
Get league information and settings

**Response:**
```json
{
  "league_id": "12345",
  "name": "My League",
  "num_teams": 10,
  "current_week": 5,
  "scoring_type": "category",
  "categories": ["FG%", "FT%", "3PM", "PTS", "REB", "AST", "STL", "BLK", "TO"]
}
```

### GET `/yahoo/players/available`
Get all available (undrafted/FA) players

**Query Parameters:**
- `position` (optional): Filter by position (PG, SG, SF, PF, C)
- `limit` (optional): Maximum results (default: 100)

**Response:**
```json
{
  "players": [
    {
      "player_id": "5479",
      "name": "LeBron James",
      "team": "LAL",
      "positions": ["SF", "PF"],
      "status": "available"
    }
  ]
}
```

---

## Players

### GET `/players/search`
Search for players by name

**Query Parameters:**
- `query` (required): Search term
- `limit` (optional): Max results (default: 20)

**Response:**
```json
[
  {
    "player_id": "5479",
    "name": "LeBron James",
    "team": "LAL",
    "positions": ["SF", "PF"]
  }
]
```

### GET `/players/{player_id}`
Get detailed player information

**Response:**
```json
{
  "player_id": "5479",
  "name": "LeBron James",
  "team": "LAL",
  "positions": ["SF", "PF"],
  "stats": {
    "FG%": 0.525,
    "FT%": 0.734,
    "3PM": 1.8,
    "PTS": 25.7,
    "REB": 7.3,
    "AST": 7.3,
    "STL": 1.3,
    "BLK": 0.5,
    "TO": 3.5
  },
  "z_scores": {
    "FG%_z": 1.2,
    "FT%_z": -0.5,
    "3PM_z": 0.8,
    "PTS_z": 2.5,
    "REB_z": 1.1,
    "AST_z": 1.8,
    "STL_z": 1.0,
    "BLK_z": -0.2,
    "TO_z": -1.5,
    "total_z": 6.2
  }
}
```

### GET `/players/{player_id}/stats`
Get player statistics

**Query Parameters:**
- `season` (optional): Season year (default: current)

**Response:**
```json
{
  "player_id": "5479",
  "season": "2024-25",
  "games_played": 45,
  "stats": {
    "FG%": 0.525,
    "FT%": 0.734,
    "3PM": 1.8,
    "PTS": 25.7,
    "REB": 7.3,
    "AST": 7.3,
    "STL": 1.3,
    "BLK": 0.5,
    "TO": 3.5
  }
}
```

### GET `/players/rankings/category`
Get player rankings by specific category

**Query Parameters:**
- `category` (required): One of FG%, FT%, 3PM, PTS, REB, AST, STL, BLK, TO
- `limit` (optional): Max results (default: 50)

**Response:**
```json
[
  {
    "rank": 1,
    "player_id": "6583",
    "name": "Nikola Jokic",
    "value": 10.5,
    "category_value": 2.8
  }
]
```

---

## Team Management

### GET `/team/roster`
Get your current team roster

**Response:**
```json
{
  "roster": [
    {
      "player_id": "5479",
      "name": "LeBron James",
      "position": "SF",
      "status": "active"
    }
  ],
  "total_players": 13
}
```

### GET `/team/standings`
Get league standings

**Response:**
```json
[
  {
    "team_id": "1",
    "team_name": "My Team",
    "rank": 3,
    "wins": 5,
    "losses": 2,
    "ties": 0
  }
]
```

### GET `/team/matchup/current`
Get current week's matchup

**Response:**
```json
{
  "week": 5,
  "opponent": {
    "team_id": "4",
    "team_name": "Opponent Team"
  },
  "categories": {
    "FG%": {"my_team": 0.468, "opponent": 0.455, "winning": true},
    "FT%": {"my_team": 0.812, "opponent": 0.798, "winning": true},
    "3PM": {"my_team": 32, "opponent": 45, "winning": false}
  }
}
```

### POST `/team/lineup/optimize`
Get optimized lineup recommendation

**Request Body:**
```json
{
  "date": "2024-10-20",
  "strategy": "maximize_games"
}
```

**Response:**
```json
{
  "lineup": {
    "PG": {"player_id": "5479", "name": "LeBron James"},
    "SG": {"player_id": "6583", "name": "Nikola Jokic"}
  },
  "games_scheduled": 8,
  "recommendations": ["Move Player X to bench - not playing today"]
}
```

---

## Draft Mode

### POST `/draft/start`
Start a new draft session

**Query Parameters:**
- `draft_position` (required): Your position (1-10)
- `snake` (optional): Snake draft format (default: true)

**Response:**
```json
{
  "session_id": "draft_abc123",
  "draft_position": 5,
  "snake": true,
  "status": "active",
  "created_at": "2024-10-20T10:00:00Z"
}
```

### GET `/draft/recommendations`
Get draft pick recommendations

**Query Parameters:**
- `session_id` (required): Draft session ID
- `current_pick` (optional): Current overall pick number
- `available_players` (optional): List of player IDs still available

**Response:**
```json
[
  {
    "rank": 1,
    "player": {
      "player_id": "6583",
      "name": "Nikola Jokic",
      "positions": ["C"]
    },
    "value": 10.5,
    "category_scores": {
      "FG%_z": 2.5,
      "FT%_z": 1.2,
      "PTS_z": 2.8
    },
    "reasoning": "Elite all-around center, fills positional need"
  }
]
```

### POST `/draft/pick`
Record a draft pick

**Request Body:**
```json
{
  "session_id": "draft_abc123",
  "player_id": "6583",
  "pick_number": 5,
  "team_id": "my_team"
}
```

**Response:**
```json
{
  "success": true,
  "pick_number": 5,
  "player_id": "6583",
  "updated_recommendations": [...]
}
```

### GET `/draft/board`
Get current draft board state

**Query Parameters:**
- `session_id` (required): Draft session ID

**Response:**
```json
{
  "session_id": "draft_abc123",
  "current_pick": 15,
  "picks": [
    {"pick": 1, "player_id": "6583", "team_id": "team_1"},
    {"pick": 2, "player_id": "5479", "team_id": "team_2"}
  ],
  "available_count": 285,
  "my_roster": ["6583", "5479"]
}
```

---

## Recommendations

### GET `/recommendations/pickups`
Get recommended waiver wire pickups

**Query Parameters:**
- `limit` (optional): Max results (default: 10)
- `position` (optional): Filter by position

**Response:**
```json
[
  {
    "player": {
      "player_id": "12345",
      "name": "Emerging Player",
      "team": "BKN",
      "positions": ["SG", "SF"]
    },
    "value": 3.5,
    "reasoning": "Fills 3PM and STL needs, trending up",
    "suggested_drop": {
      "player_id": "67890",
      "name": "Bench Warmer"
    }
  }
]
```

### GET `/recommendations/drops`
Get recommended players to drop

**Response:**
```json
[
  {
    "player": {
      "player_id": "67890",
      "name": "Bench Warmer"
    },
    "value": -1.2,
    "reasoning": "Negative value in most categories, better options available"
  }
]
```

### GET `/recommendations/trades/analyze`
Analyze a potential trade

**Query Parameters:**
- `give_player_ids`: Comma-separated player IDs you give
- `receive_player_ids`: Comma-separated player IDs you receive

**Response:**
```json
{
  "recommendation": "accept",
  "net_value": 2.5,
  "category_impact": {
    "FG%": +0.5,
    "FT%": -0.2,
    "3PM": +1.2,
    "PTS": +0.8
  },
  "reasoning": "Improves 3PM and PTS while maintaining percentages",
  "risk_factors": ["Player X injury history"]
}
```

### GET `/recommendations/streaming`
Get streaming player recommendations

**Query Parameters:**
- `days` (optional): Days to look ahead (default: 7)

**Response:**
```json
[
  {
    "player": {
      "player_id": "11111",
      "name": "Streamer Option"
    },
    "games_this_week": 4,
    "value_per_game": 1.2,
    "best_pickup_day": "2024-10-20"
  }
]
```

### GET `/recommendations/lineup/daily`
Get optimal lineup for today

**Response:**
```json
{
  "date": "2024-10-20",
  "lineup": {
    "PG": {"player_id": "5479", "games_today": 1},
    "BENCH": [{"player_id": "67890", "games_today": 0}]
  },
  "changes": [
    "Move Player X to starting lineup - has game today",
    "Bench Player Y - no game scheduled"
  ]
}
```

---

## Error Responses

All endpoints may return these error formats:

**400 Bad Request:**
```json
{
  "detail": "Invalid parameter: position must be one of PG, SG, SF, PF, C"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```json
{
  "detail": "Player not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error",
  "error_id": "abc123"
}
```

---

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Yahoo API**: Subject to Yahoo's rate limits (10,000 requests/day)

## Webhooks (Future)

Coming soon: Subscribe to events like:
- New waiver wire recommendations
- Trade offers received
- Lineup optimization alerts

---

*Last Updated: October 2025*
