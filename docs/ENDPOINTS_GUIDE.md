# API Endpoints Reference - Data Integration Layer

This guide shows how to use the newly implemented endpoints that connect Yahoo Fantasy API with the analytics engine.

## 🎯 Draft Mode Endpoints

### Start a Draft Session

```bash
POST /api/v1/draft/start
```

**Parameters:**
- `league_key` (required): Your Yahoo league key (e.g., "nba.l.12345")
- `draft_position` (required): Your draft position (1-10)
- `snake` (optional): Snake draft format (default: true)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/draft/start?league_key=nba.l.12345&draft_position=3"
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "league_key": "nba.l.12345",
  "draft_position": 3,
  "snake": true,
  "status": "active",
  "current_round": 1,
  "roster": []
}
```

---

### Get Draft Recommendations

```bash
GET /api/v1/draft/recommendations
```

**Parameters:**
- `session_id` (required): Draft session ID from /start
- `league_key` (optional): League key if no session
- `limit` (optional): Number of recommendations (default: 10)

**Example:**
```bash
curl "http://localhost:8000/api/v1/draft/recommendations?session_id=550e8400-e29b-41d4-a716-446655440000&limit=5"
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "league_key": "nba.l.12345",
  "count": 5,
  "context": {
    "roster_size": 3,
    "punting": ["TO"],
    "categories": ["FG%", "FT%", "3PM", "PTS", "REB", "AST", "STL", "BLK", "TO"]
  },
  "recommendations": [
    {
      "player_id": "5479",
      "name": "Nikola Jokic",
      "team": "DEN",
      "position": "C",
      "rank": 1,
      "total_value": 8.45,
      "z_scores": {
        "FG%": 1.2,
        "FT%": 0.8,
        "3PM": 0.3,
        "PTS": 2.1,
        "REB": 2.5,
        "AST": 1.8,
        "STL": 0.5,
        "BLK": 0.3,
        "TO": -0.5
      },
      "stats": {
        "FG%": 54.6,
        "FT%": 84.7,
        "3PM": 193,
        "PTS": 1531,
        "REB": 841,
        "AST": 625,
        "STL": 86,
        "BLK": 58,
        "TO": 209
      }
    }
  ]
}
```

---

### Record a Pick

```bash
POST /api/v1/draft/pick
```

**Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "player_id": "5479",
  "player_name": "Nikola Jokic",
  "pick_number": 3,
  "round": 1,
  "team_id": null  // null = your pick, otherwise specify team
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "pick_recorded": {
    "player_id": "5479",
    "player_name": "Nikola Jokic",
    "pick_number": 3,
    "round": 1,
    "is_my_pick": true
  },
  "roster_size": 1
}
```

---

## 🏀 Player Endpoints

### Search Players

```bash
GET /api/v1/players/search
```

**Parameters:**
- `league_key` (required): League key
- `query` (required): Player name to search
- `limit` (optional): Max results (default: 20)

**Example:**
```bash
curl "http://localhost:8000/api/v1/players/search?league_key=nba.l.12345&query=LeBron&limit=5"
```

**Response:**
```json
{
  "query": "LeBron",
  "count": 1,
  "players": [
    {
      "player_id": "3704",
      "name": "LeBron James",
      "team": "LAL",
      "position": "SF,PF",
      "total_value": 6.2,
      "z_scores": {
        "FG%": 0.9,
        "FT%": -0.2,
        "3PM": 0.8,
        "PTS": 1.5,
        "REB": 1.2,
        "AST": 1.3,
        "STL": 0.6,
        "BLK": 0.1,
        "TO": -0.4
      },
      "stats": { ... }
    }
  ]
}
```

---

### Get Overall Rankings

```bash
GET /api/v1/players/rankings
```

**Parameters:**
- `league_key` (required): League key
- `limit` (optional): Number of players (default: 50)

**Example:**
```bash
curl "http://localhost:8000/api/v1/players/rankings?league_key=nba.l.12345&limit=10"
```

**Response:**
```json
{
  "count": 10,
  "scoring_system": "9-category Z-score",
  "rankings": [
    {
      "rank": 1,
      "player_id": "5479",
      "name": "Nikola Jokic",
      "total_value": 8.45,
      ...
    },
    {
      "rank": 2,
      "player_id": "6583",
      "name": "Luka Doncic",
      "total_value": 7.89,
      ...
    }
  ]
}
```

---

### Get Category Rankings

```bash
GET /api/v1/players/rankings/category/{category}
```

**Valid Categories:** FG%, FT%, 3PM, PTS, REB, AST, STL, BLK, TO

**Example:**
```bash
curl "http://localhost:8000/api/v1/players/rankings/category/PTS?league_key=nba.l.12345&limit=10"
```

**Response:**
```json
{
  "category": "PTS",
  "count": 10,
  "rankings": [
    {
      "rank": 1,
      "name": "Joel Embiid",
      "stats": {
        "PTS": 2183
      },
      "z_scores": {
        "PTS": 3.2
      }
    }
  ]
}
```

---

### Get Available Players with Analysis

```bash
GET /api/v1/players/available
```

**Parameters:**
- `league_key` (required): League key
- `position` (optional): Filter by position (PG, SG, SF, PF, C)
- `limit` (optional): Max players (default: 100)

**Example:**
```bash
curl "http://localhost:8000/api/v1/players/available?league_key=nba.l.12345&position=C&limit=20"
```

**Response:**
```json
{
  "league_key": "nba.l.12345",
  "position_filter": "C",
  "count": 20,
  "players": [
    {
      "player_id": "6450",
      "name": "Clint Capela",
      "team": "ATL",
      "position": "C",
      "ownership": 0,
      "total_value": 3.8,
      "z_scores": {
        "FG%": 2.1,
        "FT%": -1.2,
        "3PM": -0.5,
        "PTS": 0.5,
        "REB": 2.0,
        "AST": -0.3,
        "STL": 0.2,
        "BLK": 1.5,
        "TO": 0.3
      },
      "stats": { ... }
    }
  ]
}
```

---

## 📊 Understanding the Response Data

### Z-Scores
- **Positive values** = Above average performance
- **Negative values** = Below average performance
- **0** = League average
- **±1.0** = About 1 standard deviation from average
- **±2.0** = Elite or very poor

### Total Value
Sum of all category Z-scores, representing overall fantasy value.

### Categories
- **FG%**: Field Goal Percentage (weighted by volume)
- **FT%**: Free Throw Percentage (weighted by volume)
- **3PM**: Three-Pointers Made
- **PTS**: Points
- **REB**: Rebounds
- **AST**: Assists
- **STL**: Steals
- **BLK**: Blocks
- **TO**: Turnovers (inverted - lower is better)

---

## 🔑 Authentication

All endpoints require Yahoo OAuth authentication. Make sure you:

1. Have completed OAuth flow (see `YAHOO_QUICKSTART.md`)
2. Have valid access token in `backend/.env`
3. Token is not expired (use refresh if needed)

---

## 🧪 Testing

Run the integration test suite:

```bash
python test_data_integration.py
```

This will test:
- ✅ Data mapper with sample responses
- ✅ Yahoo API connection
- ✅ Player data service methods
- ✅ Analytics engine calculations

---

## 🚀 Quick Start Workflow

### Draft Mode
1. **Start session**: `POST /draft/start` with league_key and position
2. **Get recommendations**: `GET /draft/recommendations` with session_id
3. **Record pick**: `POST /draft/pick` when you or others pick
4. **Repeat steps 2-3** until draft complete

### Player Research
1. **Search**: `GET /players/search?query=LeBron` to find specific players
2. **Rankings**: `GET /players/rankings` to see top overall players
3. **Category**: `GET /players/rankings/category/PTS` for category specialists
4. **Available**: `GET /players/available?position=C` for waiver wire options

---

## 💡 Tips

1. **Use session_id** to maintain draft context and get personalized recommendations
2. **Check z_scores** to identify category strengths/weaknesses
3. **Filter by position** on /available endpoint for targeted waiver searches
4. **Monitor total_value** as a quick overall quality metric
5. **Punt strategies** are auto-detected from your roster composition

---

## 📝 Next Steps

- [ ] Test endpoints with your Yahoo league
- [ ] Review recommendations and validate they make sense
- [ ] Try different punt strategies by drafting specific player types
- [ ] Use category rankings to find specialists
- [ ] Check available players for waiver wire targets
