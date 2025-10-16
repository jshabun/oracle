# 🎯 Draft Mode Quick Start

A step-by-step guide to using Oracle for your fantasy basketball draft.

## Prerequisites

✅ Docker running  
✅ Yahoo OAuth completed (`test_oauth.py`)  
✅ Access token in `backend/.env`  
✅ Services started (`docker-compose up`)

---

## Step 1: Get Your League Key

### Option A: From Yahoo URL

Your Yahoo league URL looks like:
```
https://basketball.fantasysports.yahoo.com/nba/12345
                                                 ^^^^^
```

Your league key is: `nba.l.12345`

### Option B: Via API

```bash
curl "http://localhost:8000/api/v1/yahoo/leagues"
```

Look for `league_key` in the response.

---

## Step 2: Start a Draft Session

```bash
curl -X POST "http://localhost:8000/api/v1/draft/start?league_key=nba.l.12345&draft_position=3" \
  | jq
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "league_key": "nba.l.12345",
  "draft_position": 3,
  "status": "active"
}
```

**Save the `session_id`!** You'll need it for all draft operations.

---

## Step 3: Get Your First Recommendations

```bash
curl "http://localhost:8000/api/v1/draft/recommendations?session_id=550e8400-e29b-41d4-a716-446655440000&limit=10" \
  | jq
```

**What You'll See:**

```json
{
  "recommendations": [
    {
      "rank": 1,
      "name": "Nikola Jokic",
      "team": "DEN",
      "position": "C",
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
      "stats": { ... }
    },
    // ... 9 more players
  ]
}
```

### Reading the Results

- **total_value**: Overall fantasy value (higher = better)
- **z_scores**: Performance in each category
  - Positive = Above average
  - Negative = Below average
  - 0 = League average
  - ±1.0 = 1 standard deviation
  - ±2.0 = Elite/poor

---

## Step 4: Record Picks

### Your Pick

```bash
curl -X POST "http://localhost:8000/api/v1/draft/pick" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "player_id": "5479",
    "player_name": "Nikola Jokic",
    "pick_number": 3,
    "round": 1
  }' | jq
```

### Other Team's Pick

```bash
curl -X POST "http://localhost:8000/api/v1/draft/pick" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "player_id": "6583",
    "player_name": "Luka Doncic",
    "pick_number": 1,
    "round": 1,
    "team_id": "team_1"
  }' | jq
```

**Why record other picks?**  
Future enhancement will exclude drafted players from recommendations.

---

## Step 5: Get Updated Recommendations

After each pick, get fresh recommendations:

```bash
curl "http://localhost:8000/api/v1/draft/recommendations?session_id=550e8400-e29b-41d4-a716-446655440000&limit=10" \
  | jq
```

The system will:
- ✅ Analyze your current roster
- ✅ Detect punt strategies automatically
- ✅ Suggest players that complement your team
- ✅ Balance positional needs

---

## Step 6: Review Your Draft Board

```bash
curl "http://localhost:8000/api/v1/draft/board?session_id=550e8400-e29b-41d4-a716-446655440000" \
  | jq
```

See:
- Your roster
- Current round
- Detected punt categories
- Draft position

---

## 🔍 Advanced Features

### Search for Specific Players

```bash
curl "http://localhost:8000/api/v1/players/search?league_key=nba.l.12345&query=LeBron" \
  | jq
```

### Category-Specific Rankings

```bash
# Top scorers
curl "http://localhost:8000/api/v1/players/rankings/category/PTS?league_key=nba.l.12345&limit=20" \
  | jq

# Best rebounders
curl "http://localhost:8000/api/v1/players/rankings/category/REB?league_key=nba.l.12345&limit=20" \
  | jq

# Best three-point shooters
curl "http://localhost:8000/api/v1/players/rankings/category/3PM?league_key=nba.l.12345&limit=20" \
  | jq
```

### Overall Rankings

```bash
curl "http://localhost:8000/api/v1/players/rankings?league_key=nba.l.12345&limit=50" \
  | jq
```

---

## 📊 Understanding Punt Strategies

### What is Punting?

**Punting** = Intentionally ignoring certain categories to dominate others.

**Example:** Punt FG% and TO  
- Draft high-volume shooters (Harden, Young)
- Don't worry about efficiency
- Focus on points, assists, threes

### How Oracle Detects Punts

After 3+ picks, if you're consistently weak in a category (Z-score < -0.5), Oracle will:
1. Flag it as a punt category
2. Recommend players who excel in other areas
3. De-prioritize that category in recommendations

### Common Punt Strategies

| Punt | Target Stats | Example Players |
|------|-------------|-----------------|
| FG% | 3PM, PTS, AST | Trae Young, Damian Lillard |
| TO | AST, STL | Russell Westbrook, LaMelo Ball |
| FT% | REB, BLK | Clint Capela, Rudy Gobert |
| 3PM | FG%, REB, BLK | Domantas Sabonis, Bam Adebayo |

---

## 🎯 Draft Day Workflow

### 1. Pre-Draft Setup (10 minutes before)

```bash
# Start services
docker-compose up -d

# Verify OAuth
python test_oauth.py

# Start draft session
curl -X POST "http://localhost:8000/api/v1/draft/start?league_key=nba.l.12345&draft_position=3"
```

### 2. During Draft (Each Round)

```bash
# 1. Get recommendations
curl "http://localhost:8000/api/v1/draft/recommendations?session_id=<ID>&limit=10"

# 2. Make your pick (use the API or Yahoo directly)

# 3. Record the pick
curl -X POST "http://localhost:8000/api/v1/draft/pick" -d '{ ... }'

# 4. Repeat for next round
```

### 3. Between Your Picks

While waiting for your turn:

```bash
# Check specific categories
curl "http://localhost:8000/api/v1/players/rankings/category/REB?league_key=nba.l.12345&limit=10"

# Search for targets
curl "http://localhost:8000/api/v1/players/search?league_key=nba.l.12345&query=Anthony"

# Review your board
curl "http://localhost:8000/api/v1/draft/board?session_id=<ID>"
```

---

## 💡 Pro Tips

### 1. Use Swagger UI for Easier Testing

Open: http://localhost:8000/docs

- Visual interface for all endpoints
- Auto-fills parameters
- Shows response schemas
- Test without curl

### 2. Save Your Session ID

Create a shell variable:
```bash
export SESSION_ID="550e8400-e29b-41d4-a716-446655440000"

# Now use it
curl "http://localhost:8000/api/v1/draft/recommendations?session_id=$SESSION_ID&limit=10"
```

### 3. Use jq for Pretty Output

```bash
# Install jq
sudo apt-get install jq  # Ubuntu/Debian
brew install jq          # macOS

# Pipe all responses through it
curl "..." | jq
```

### 4. Create Aliases

Add to `~/.bashrc`:
```bash
alias draft-recs='curl "http://localhost:8000/api/v1/draft/recommendations?session_id=$SESSION_ID&limit=10" | jq'
alias draft-board='curl "http://localhost:8000/api/v1/draft/board?session_id=$SESSION_ID" | jq'
alias search-player='curl "http://localhost:8000/api/v1/players/search?league_key=nba.l.12345&query="'
```

Then just run:
```bash
draft-recs
draft-board
search-player "LeBron"
```

### 5. Monitor in Real-Time

Open multiple terminals:
- **Terminal 1:** Docker logs (`docker-compose logs -f backend`)
- **Terminal 2:** Draft recommendations
- **Terminal 3:** Quick searches

---

## 🐛 Troubleshooting

### "401 Unauthorized"
- OAuth token expired
- Run `python test_oauth.py` to refresh

### "404 Draft session not found"
- Session ID incorrect or expired
- Sessions stored in memory (lost on restart)
- Create new session

### "No players returned"
- League has no available players
- Check league_key is correct
- Verify league exists and is active

### "Rate limit exceeded"
- Yahoo API limits: 10k requests/day
- Wait or use cached data
- Reduce limit parameter

---

## 📚 Next Steps

After mastering draft mode:

1. **Season Management** - Waiver wire recommendations (coming soon)
2. **Trade Analyzer** - Evaluate trade offers (coming soon)
3. **Lineup Optimizer** - Daily lineup suggestions (coming soon)

---

## ❓ FAQ

**Q: Can I use this during a live Yahoo draft?**  
A: Yes! Run the API locally and make picks in Yahoo, then record them via API.

**Q: Does this auto-draft for me?**  
A: No. It provides recommendations; you make the final decision.

**Q: How accurate are the recommendations?**  
A: Based on Z-scores, which are statistically sound. Accuracy depends on your strategy and league settings.

**Q: Can I customize the categories?**  
A: Currently uses 9-cat (FG%, FT%, 3PM, PTS, REB, AST, STL, BLK, TO). Custom categories coming soon.

**Q: Does it work for other sports?**  
A: Built for basketball. Could be adapted for other Yahoo fantasy sports.

---

**Ready to dominate your draft?** Fire up the API and start your session! 🏀🔥
