# Yahoo OAuth Setup Guide

## Complete Step-by-Step Tutorial

This guide will walk you through setting up Yahoo OAuth for your Fantasy Basketball Oracle.

---

## Part 1: Get Yahoo API Credentials (10 minutes)

### Step 1: Create Yahoo Developer Account

1. Go to https://developer.yahoo.com/
2. Sign in with your Yahoo account
3. Accept the Terms of Service

### Step 2: Create an Application

1. Visit https://developer.yahoo.com/apps/
2. Click **"Create an App"** button
3. Fill in the application form:

#### Application Details:
```
Application Name: Fantasy Basketball Oracle
Description: AI-powered fantasy basketball assistant for managing my team
Home Page URL: http://localhost:3000
Redirect URI(s): http://localhost:8000/api/v1/yahoo/callback
```

#### API Permissions:
- ✅ Check **"Fantasy Sports"**
- ✅ Select **"Read"** (and "Read/Write" if you want to make trades/lineup changes)

#### Application Type:
- Select **"Web Application"**

4. Click **"Create App"**

### Step 3: Get Your Credentials

After creating the app, you'll see:
- **Client ID (Consumer Key)**: A long string like `dj0yJmk9aBcDeFgH...`
- **Client Secret (Consumer Secret)**: Another long string

**⚠️ IMPORTANT**: Keep these secret! Never commit them to git.

---

## Part 2: Configure Your Application (5 minutes)

### Step 1: Set Environment Variables

```bash
cd /workspaces/oracle

# Copy the example file
cp backend/.env.example backend/.env

# Edit the file
nano backend/.env
```

### Step 2: Add Your Credentials

Replace the placeholder values:

```env
# Yahoo Fantasy API Credentials
YAHOO_CONSUMER_KEY=dj0yJmk9aBcDeFgH...  # Your Client ID
YAHOO_CONSUMER_SECRET=1234567890abcdef...  # Your Client Secret
YAHOO_LEAGUE_ID=  # Leave blank for now

# Database
DATABASE_URL=postgresql://oracle:oracle@db:5432/oracle

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-random-secret-key-here

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Step 3: Find Your League ID

1. Go to your Yahoo Fantasy Basketball league
2. Look at the URL: `https://basketball.fantasysports.yahoo.com/nba/XXXXX/`
3. The `XXXXX` is your League ID
4. Add it to your `.env` file:

```env
YAHOO_LEAGUE_ID=12345
```

---

## Part 3: Test the OAuth Flow (5 minutes)

### Step 1: Start the Application

```bash
docker-compose up --build
```

Wait for all services to start (~2 minutes).

### Step 2: Open API Documentation

Visit: http://localhost:8000/docs

You'll see the interactive Swagger UI with all endpoints.

### Step 3: Get Authorization URL

1. Find the **`/api/v1/yahoo/auth/url`** endpoint
2. Click **"Try it out"**
3. Leave the default redirect_uri
4. Click **"Execute"**

You'll get a response like:
```json
{
  "auth_url": "https://api.login.yahoo.com/oauth2/request_auth?client_id=...",
  "redirect_uri": "http://localhost:8000/api/v1/yahoo/callback",
  "instructions": "Visit the auth_url to authorize the application"
}
```

### Step 4: Authorize the Application

1. **Copy the `auth_url`** from the response
2. **Open it in your browser**
3. You'll see Yahoo's authorization page
4. Click **"Agree"** to authorize

### Step 5: Handle the Callback

After authorizing, Yahoo redirects you to:
```
http://localhost:8000/api/v1/yahoo/callback?code=XXXXX
```

You should see:
```json
{
  "status": "success",
  "message": "Authorization successful! You can now use the API.",
  "expires_in": "3600 seconds"
}
```

🎉 **You're authenticated!** The token is now stored in memory.

---

## Part 4: Test API Endpoints (10 minutes)

Now that you're authenticated, test these endpoints in the Swagger UI:

### 1. Get Your Leagues

Endpoint: **`GET /api/v1/yahoo/leagues`**

Response:
```json
{
  "leagues": [
    {
      "league_key": "nba.l.12345",
      "league_id": "12345",
      "name": "My Fantasy League",
      "season": "2024",
      "num_teams": 10,
      "current_week": 5
    }
  ]
}
```

### 2. Get League Standings

Endpoint: **`GET /api/v1/yahoo/league/{league_key}/standings`**

Use your `league_key` from step 1 (e.g., `nba.l.12345`)

Response:
```json
{
  "standings": [
    {
      "team_key": "nba.l.12345.t.1",
      "team_id": "1",
      "name": "My Team",
      "rank": 3,
      "wins": 5,
      "losses": 2
    }
  ]
}
```

### 3. Get Available Players

Endpoint: **`GET /api/v1/yahoo/league/{league_key}/players/available`**

Parameters:
- `league_key`: Your league key
- `position`: PG, SG, SF, PF, C (optional)
- `count`: 25 (default)

Response:
```json
{
  "players": [
    {
      "player_key": "nba.p.5479",
      "name": "LeBron James",
      "positions": ["SF", "PF"],
      "team": "LAL",
      "status": "available"
    }
  ]
}
```

### 4. Search for Players

Endpoint: **`GET /api/v1/yahoo/league/{league_key}/players/search`**

Parameters:
- `league_key`: Your league key
- `query`: "LeBron" or "Curry"

### 5. Get Your Team Roster

Endpoint: **`GET /api/v1/yahoo/team/{team_key}/roster`**

Use your `team_key` from the standings (e.g., `nba.l.12345.t.1`)

Response:
```json
{
  "roster": [
    {
      "player_key": "nba.p.5479",
      "name": "LeBron James",
      "positions": ["SF", "PF"],
      "selected_position": "SF",
      "team": "LAL"
    }
  ]
}
```

### 6. Get Player Stats

Endpoint: **`GET /api/v1/yahoo/player/{player_key}/stats`**

Use a player_key from your roster (e.g., `nba.p.5479`)

---

## Part 5: Token Management

### Check Token Status

Endpoint: **`GET /api/v1/yahoo/tokens/status`**

Response:
```json
{
  "authenticated": true,
  "expires_at": "2024-10-20T12:00:00",
  "has_refresh_token": true
}
```

### Refresh Token (if expired)

Endpoint: **`POST /api/v1/yahoo/tokens/refresh`**

The system will automatically refresh tokens when they expire, but you can manually trigger it.

---

## Part 6: Integrate with Frontend

### Create API Client

Create `frontend/src/services/yahoo.js`:

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

class YahooService {
  async getAuthUrl() {
    const response = await axios.get(`${API_URL}/yahoo/auth/url`);
    return response.data;
  }

  async getLeagues() {
    const response = await axios.get(`${API_URL}/yahoo/leagues`);
    return response.data;
  }

  async getAvailablePlayers(leagueKey, position = null) {
    const params = position ? { position } : {};
    const response = await axios.get(
      `${API_URL}/yahoo/league/${leagueKey}/players/available`,
      { params }
    );
    return response.data;
  }

  async searchPlayers(leagueKey, query) {
    const response = await axios.get(
      `${API_URL}/yahoo/league/${leagueKey}/players/search`,
      { params: { query } }
    );
    return response.data;
  }

  async getTeamRoster(teamKey) {
    const response = await axios.get(
      `${API_URL}/yahoo/team/${teamKey}/roster`
    );
    return response.data;
  }
}

export default new YahooService();
```

### Use in React Components

```javascript
import { useState, useEffect } from 'react';
import yahooService from '../services/yahoo';

function Dashboard() {
  const [leagues, setLeagues] = useState([]);

  useEffect(() => {
    async function fetchLeagues() {
      try {
        const data = await yahooService.getLeagues();
        setLeagues(data.leagues);
      } catch (error) {
        console.error('Failed to fetch leagues:', error);
      }
    }
    fetchLeagues();
  }, []);

  return (
    <div>
      {leagues.map(league => (
        <div key={league.league_key}>
          {league.name} - {league.num_teams} teams
        </div>
      ))}
    </div>
  );
}
```

---

## Troubleshooting

### Issue: "Yahoo API credentials not configured"

**Solution**: Check that your `.env` file has the correct credentials:
```bash
cat backend/.env | grep YAHOO
```

### Issue: "Authorization failed"

**Possible causes**:
1. **Redirect URI mismatch**: Must exactly match what you set in Yahoo Developer Console
2. **Wrong credentials**: Double-check Consumer Key/Secret
3. **Code expired**: Authorization codes expire in 10 minutes, start over

### Issue: "Token expired"

**Solution**: The system should auto-refresh, but you can manually refresh:
```bash
curl -X POST http://localhost:8000/api/v1/yahoo/tokens/refresh
```

### Issue: "API request failed: 401"

**Solution**: You need to re-authorize:
1. Get new auth URL
2. Visit it and authorize
3. Complete the callback

### Issue: Can't access endpoints

**Solution**: Check if backend is running:
```bash
docker-compose ps
curl http://localhost:8000/health
```

---

## Production Considerations

### Token Storage

Currently, tokens are stored in memory (lost on restart). For production:

1. **Store tokens in database** per user
2. **Implement user authentication** (login system)
3. **Associate Yahoo tokens with user accounts**

Example database model:
```python
class User(Base):
    id = Column(Integer, primary_key=True)
    yahoo_access_token = Column(String)
    yahoo_refresh_token = Column(String)
    yahoo_token_expires_at = Column(DateTime)
```

### Security

1. **Use HTTPS** in production (not http://localhost)
2. **Update redirect URI** to your domain:
   ```
   https://yourdomain.com/api/v1/yahoo/callback
   ```
3. **Set strong SECRET_KEY** in `.env`
4. **Rotate tokens regularly**

### Rate Limiting

Yahoo API limits:
- **10,000 requests per day** per application
- Be mindful of request frequency
- Cache responses when possible

---

## Next Steps

Now that Yahoo OAuth is working, you can:

1. ✅ Fetch real league data
2. ✅ Get player statistics
3. ✅ Pull available players for draft
4. ✅ Access your team roster

**Next implementation**: Connect this data to your analytics engine!

See **`docs/DATA_INTEGRATION.md`** for the next steps.

---

## Quick Reference

### Important URLs

- **Yahoo Developer Console**: https://developer.yahoo.com/apps/
- **Yahoo Fantasy API Docs**: https://developer.yahoo.com/fantasysports/guide/
- **Your API Docs**: http://localhost:8000/docs
- **Your Frontend**: http://localhost:3000

### Key Endpoints

```bash
# Get auth URL
GET /api/v1/yahoo/auth/url

# OAuth callback (automatic)
GET /api/v1/yahoo/callback?code=XXX

# Get leagues
GET /api/v1/yahoo/leagues

# Get available players
GET /api/v1/yahoo/league/{league_key}/players/available

# Get roster
GET /api/v1/yahoo/team/{team_key}/roster

# Check auth status
GET /api/v1/yahoo/tokens/status
```

---

**Congratulations!** You've successfully integrated Yahoo OAuth! 🎉

Your Fantasy Basketball Oracle can now access real Yahoo Fantasy data!
