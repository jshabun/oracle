# Architecture Overview

**Last Updated:** January 2025 | **Status:** Data Integration Complete ✅

## 🎉 Recent Updates

**Version 0.2.0 - Data Integration Layer Complete:**
- ✅ `YahooDataMapper` - Parses Yahoo API responses to PlayerStats
- ✅ `PlayerDataService` - Bridges Yahoo API with analytics engine  
- ✅ Real draft recommendations using actual Yahoo player data
- ✅ Player search, rankings, and category analysis
- ✅ 26 working API endpoints across 5 modules

## System Design

The Fantasy Basketball Oracle is built as a microservices architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                       │
│                      (React Frontend)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (REST + WebSocket)            │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Business Logic Layer                │  │
│  │  - Draft Engine    - Analytics Engine                │  │
│  │  - Trade Analyzer  - Lineup Optimizer                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              External Services Layer                  │  │
│  │  - Yahoo Fantasy API  - NBA Stats API                │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────┬───────────────────────┬─────────────────────┘
                │                       │
                ▼                       ▼
    ┌────────────────────┐  ┌────────────────────┐
    │   PostgreSQL DB    │  │    Redis Cache     │
    │  - League Data     │  │  - Session Data    │
    │  - Player Stats    │  │  - Task Queue      │
    │  - User Data       │  │                    │
    └────────────────────┘  └────────────────────┘
                                        │
                                        ▼
                            ┌────────────────────┐
                            │   Celery Workers   │
                            │  - Data Updates    │
                            │  - Projections     │
                            └────────────────────┘
```

## Core Components

### 1. Analytics Engine (`app/core/analytics.py`)
**Purpose**: Calculate player values and rankings

**Key Classes**:
- `PlayerStats`: Data model for player statistics
- `CategoryAnalyzer`: Z-score calculations across 9 categories
- `DraftEngine`: Draft recommendations and team building

**Algorithm Flow**:
1. Load player stats from database/API
2. Filter by minimum games played
3. Calculate Z-scores for each category:
   - Counting stats: Standard Z-score (value - mean) / std
   - Percentages: Weighted by volume (attempts)
   - Turnovers: Inverted (negative is good)
4. Sum Z-scores for total player value
5. Adjust for positional scarcity
6. Generate recommendations

### 2. Yahoo Fantasy Integration
**OAuth Flow**:
```
User → Request Auth → Yahoo Login → Callback → Token Exchange → API Access
```

**Data Fetched**:
- League settings and roster requirements
- Current roster and lineup
- Available players
- Game schedules
- Matchup information
- Transaction history

### 3. Draft Mode System

**State Management**:
```python
DraftSession:
  - session_id
  - league_id
  - draft_position
  - snake_draft
  - current_pick
  - picked_players []
  - team_roster []
  - available_players []
```

**Recommendation Logic**:
1. Get available players
2. Calculate Z-scores for all available
3. Analyze current roster composition
4. Identify category gaps
5. Apply positional scarcity modifiers
6. Rank by adjusted value
7. Return top N recommendations

### 4. Season Management

**Waiver Wire Recommendations**:
- Find available players above replacement level
- Compare against weakest roster players
- Consider category needs
- Factor in schedule (games remaining)
- Respect acquisition limit (5/week)

**Lineup Optimization**:
- Fetch daily game schedule
- Identify which players are playing
- Optimize for maximum games
- Consider rest/injury reports
- Balance category production

**Trade Analysis**:
```python
def analyze_trade(give_players, receive_players):
    current_z = team_z_scores(current_roster)
    new_z = team_z_scores(current_roster - give + receive)
    
    impact = {
        category: new_z[cat] - current_z[cat]
        for cat in categories
    }
    
    recommendation = "accept" if sum(impact.values()) > threshold
    return recommendation, impact
```

## Database Schema

### Players Table
```sql
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    yahoo_id VARCHAR UNIQUE,
    name VARCHAR,
    team VARCHAR,
    position VARCHAR[],
    stats JSONB,
    projections JSONB,
    last_updated TIMESTAMP
);
```

### Teams Table
```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    league_id VARCHAR,
    roster_player_ids INTEGER[],
    transactions JSONB[],
    created_at TIMESTAMP
);
```

### Draft Sessions Table
```sql
CREATE TABLE draft_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    draft_position INTEGER,
    picks JSONB[],
    recommendations_log JSONB,
    created_at TIMESTAMP
);
```

## API Architecture

### REST Endpoints
- `/api/v1/yahoo/*` - Yahoo Fantasy integration
- `/api/v1/players/*` - Player data and search
- `/api/v1/team/*` - Team management
- `/api/v1/draft/*` - Draft mode
- `/api/v1/recommendations/*` - Waiver/trade/lineup suggestions

### WebSocket Channels
- `/ws/draft/{session_id}` - Real-time draft updates
- `/ws/matchup` - Live matchup tracking

## Background Tasks (Celery)

### Periodic Tasks
```python
# Update player stats daily at 3 AM
@celery.task
def update_player_stats():
    fetch_from_yahoo_api()
    calculate_projections()
    update_database()

# Check lineup every hour during game days
@celery.task
def check_lineup_optimization():
    for user in active_users:
        if needs_optimization(user):
            send_notification(user, recommendations)
```

### Task Schedule
- Player stats update: Daily at 3:00 AM
- Injury updates: Every 2 hours
- Waiver recommendations: Daily at 10:00 AM
- Lineup check: Hourly during game days

## Caching Strategy

**Redis Cache Layers**:
1. **API Response Cache** (TTL: 5 minutes)
   - Yahoo API responses
   - Player rankings
   
2. **Computation Cache** (TTL: 1 hour)
   - Z-score calculations
   - Trade analysis results
   
3. **Session Cache** (TTL: 24 hours)
   - Draft sessions
   - User preferences

## Security Considerations

1. **OAuth Tokens**: Store securely, refresh automatically
2. **API Rate Limiting**: Respect Yahoo's 10,000 requests/day
3. **Input Validation**: Pydantic models for all inputs
4. **CORS**: Restrict to known frontend origins
5. **Environment Variables**: Never commit secrets

## Scalability

**Current Limitations**:
- Single server deployment
- Synchronous API calls to Yahoo
- In-memory draft sessions

**Future Improvements**:
- Horizontal scaling with load balancer
- Message queue for Yahoo API calls
- Redis for distributed draft sessions
- Read replicas for database

## Monitoring & Logging

**Logging Strategy**:
```python
import logging

logger = logging.getLogger("oracle")
logger.setLevel(logging.INFO)

# Log important events
logger.info("Draft started", extra={"session_id": session.id})
logger.warning("Yahoo API rate limit approaching")
logger.error("Failed to fetch player stats", exc_info=True)
```

**Metrics to Track**:
- API response times
- Yahoo API usage
- Draft session duration
- Recommendation accuracy
- User engagement

## Deployment Architecture

**Docker Compose Services**:
- `backend`: FastAPI application
- `frontend`: React/Vite dev server (or Nginx for prod)
- `db`: PostgreSQL database
- `redis`: Redis cache/queue
- `celery`: Background workers

**Portainer Deployment**:
1. Build images locally or in CI/CD
2. Push to container registry
3. Deploy stack via Portainer
4. Configure volumes for persistence
5. Set up health checks

## Performance Optimization

1. **Database Indexing**:
   - Index on `yahoo_id`, `name`, `team`
   - Partial index on active players
   
2. **Query Optimization**:
   - Fetch only needed columns
   - Use database-level aggregations
   - Batch updates
   
3. **Frontend Optimization**:
   - React Query for data caching
   - Lazy loading for large lists
   - Virtualized scrolling for player lists

## Testing Strategy

- **Unit Tests**: Core analytics functions
- **Integration Tests**: API endpoints
- **E2E Tests**: Draft flow, recommendations
- **Load Tests**: Yahoo API integration

---

*Last Updated: October 2025*
