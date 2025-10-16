# 🎯 Quick Reference Card

## One-Command Start

```bash
./start.sh
```

Then visit: **http://localhost:3000**

---

## Your League Settings (Configured)

- **Teams**: 10
- **Categories**: FG%, FT%, 3PM, PTS, REB, AST, STL, BLK, TO
- **Roster**: PG, SG, G, SF, PF, F, C, 3×UTIL, 3×BENCH, 2×IL, IL+
- **Acquisitions**: Max 5 per week
- **Playoffs**: Weeks 20-22
- **IST**: Weeks 5-9

---

## Key Files to Edit

### League Configuration
📄 `backend/app/core/config.py` - Change league settings

### Analytics Engine
📄 `backend/app/core/analytics.py` - Modify Z-score calculations

### API Endpoints
📄 `backend/app/api/v1/endpoints/*.py` - Add/modify endpoints

### Frontend Pages
📄 `frontend/src/pages/*.jsx` - Update UI components

---

## Useful Commands

### Start Application
```bash
docker-compose up --build
```

### Stop Application
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Reset Database
```bash
docker-compose down -v
docker-compose up
```

### Access Database
```bash
docker exec -it oracle-db psql -U oracle -d oracle
```

### Backend Only (Dev)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Only (Dev)
```bash
cd frontend
npm install
npm run dev
```

---

## API Endpoints (Ready to Use)

### Yahoo Integration
- `GET /api/v1/yahoo/auth/url` - Get OAuth URL
- `GET /api/v1/yahoo/league/info` - League details
- `GET /api/v1/yahoo/players/available` - Available players

### Draft Mode
- `POST /api/v1/draft/start` - Start draft session
- `GET /api/v1/draft/recommendations` - Get pick suggestions
- `POST /api/v1/draft/pick` - Record a pick

### Players
- `GET /api/v1/players/search` - Search players
- `GET /api/v1/players/{id}` - Player details
- `GET /api/v1/players/rankings/category` - Category rankings

### Recommendations
- `GET /api/v1/recommendations/pickups` - Waiver suggestions
- `GET /api/v1/recommendations/drops` - Drop candidates
- `GET /api/v1/recommendations/trades/analyze` - Trade analyzer

Full API docs: **http://localhost:8000/docs**

---

## Strategy Quick Tips

### Draft Strategy
1. **Rounds 1-3**: Elite players (Jokić, Giannis, Steph)
2. **Rounds 4-7**: Fill positions, establish strengths
3. **Rounds 8+**: Category specialists, upside plays

### Punt Strategies
- **Punt FT%**: Draft centers (Gobert, Capela)
- **Punt TO**: Load assists (Harden, Trae)
- **Punt 3PM**: Build around bigs
- **Balanced**: No punts, win 5-4 consistently

### Category Priorities
**High Value**: FG%, FT%, AST, STL
**Medium Value**: PTS, REB, BLK
**Lower Value**: 3PM, TO (easier to stream)

### Weekly Tactics
- **Monday**: Review weekend, plan pickups
- **Wednesday**: Execute waiver claims
- **Friday-Sunday**: Stream for volume games
- **Daily**: Check lineup (players playing today?)

---

## Z-Score Interpretation

| Z-Score | Rating | Description |
|---------|--------|-------------|
| +3.0+ | Elite | Top 5 in category |
| +2.0 to +3.0 | Excellent | Top 10-15 |
| +1.0 to +2.0 | Above Average | Top 20-40 |
| -1.0 to +1.0 | Average | Middle of pack |
| -1.0 to -2.0 | Below Average | Consider punting |
| -2.0+ | Poor | Definite punt category |

**Total Z-Score Rankings:**
- **12+**: MVP tier (Jokić, Giannis)
- **8-12**: First round
- **6-8**: Second/third round
- **4-6**: Mid rounds
- **2-4**: Late rounds
- **0-2**: Waiver wire

---

## Documentation Map

📖 **Read First**: `docs/COMPLETE_GUIDE.md` - Everything you need  
🏗️ **Architecture**: `docs/ARCHITECTURE.md` - System design  
🚀 **Setup**: `docs/GETTING_STARTED.md` - Detailed setup  
🔌 **API**: `docs/API.md` - Complete API reference  
📋 **Summary**: `docs/PROJECT_SUMMARY.md` - What we built  

---

## Deployment to Your Ubuntu Server

### Via Portainer (Recommended)

1. **Access Portainer**: http://your-server:9000
2. **Stacks** → **Add Stack**
3. **Upload** `docker-compose.yml`
4. **Environment variables**:
   ```
   YAHOO_CONSUMER_KEY=your_key
   YAHOO_CONSUMER_SECRET=your_secret
   YAHOO_LEAGUE_ID=your_league_id
   ```
5. **Deploy**

### Via Command Line

```bash
# On your Ubuntu server
git clone <your-repo>
cd oracle
cp backend/.env.example backend/.env
nano backend/.env  # Add credentials
docker-compose up -d
```

---

## Troubleshooting

### Issue: Port already in use
```bash
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
```

### Issue: Yahoo API not connecting
- Verify Consumer Key/Secret
- Check redirect URI: `http://localhost:8000/api/v1/yahoo/callback`
- Enable Fantasy Sports permission

### Issue: Database connection failed
```bash
docker-compose restart db
docker-compose logs db  # Check errors
```

### Issue: Frontend can't reach backend
- Check `VITE_API_URL` in frontend
- Verify CORS in `backend/app/core/config.py`
- Ensure backend is on port 8000

---

## Next Implementation Tasks

### Priority 1: Yahoo OAuth
📄 Create: `backend/app/services/yahoo.py`
- OAuth authentication flow
- Token storage & refresh
- API request wrapper

### Priority 2: Database Models
📄 Create: `backend/app/models/`
- Player model
- Team model
- DraftSession model

### Priority 3: Data Fetching
📄 Create: `backend/app/services/data_fetcher.py`
- Fetch player stats from Yahoo
- Update database daily
- Calculate projections

### Priority 4: Frontend API Client
📄 Create: `frontend/src/services/api.js`
- Axios client setup
- API endpoint wrappers
- Error handling

---

## Support & Resources

- **Yahoo API**: https://developer.yahoo.com/fantasysports/guide/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Docker**: https://docs.docker.com/

---

## 🏆 Success Metrics

Track these to measure your assistant's effectiveness:

- ✅ Draft picks that exceed ADP
- ✅ Waiver pickups that outperform drops
- ✅ Category matchup wins per week
- ✅ Improved league ranking
- ✅ **Championship victory!** 🎉

---

**Built with ❤️ for fantasy basketball dominance**

*Remember: The Oracle provides wisdom, but you make the final call!* 🏀
