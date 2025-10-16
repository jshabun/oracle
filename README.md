# Oracle

![Yahoo!](https://img.shields.io/badge/Yahoo!-6001D2?style=for-the-badge&logo=Yahoo!&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

A self-hosted web app that helps you **dominate your Yahoo Fantasy Basketball league**. Get real-time draft recommendations powered by statistical Z-score analysis, smart waiver wire suggestions, and data-driven roster decisions — all through a clean, interactive web interface.

## ✨ What's New

**🎉 Data Integration Complete!** The app now connects Yahoo Fantasy API with our analytics engine:

- ✅ Real player stats from your Yahoo league
- ✅ Z-score rankings across all 9 categories
- ✅ Live draft recommendations with actual data
- ✅ Player search with statistical analysis
- ✅ Category-specific rankings

## 🚀 Features

### 📊 Draft Mode

* **Live draft recommendations** during your draft with real Yahoo player data
* **Z-score analysis** across all 9 categories (FG%, FT%, 3PM, PTS, REB, AST, STL, BLK, TO)
* **Automatic punt detection** - identifies and adapts to your strategy
* **Positional scarcity** tracking for balanced team building
* **Session tracking** to maintain context throughout your draft

### 🏀 Player Analytics

* **Overall rankings** based on total fantasy value
* **Category rankings** to find specialists (top scorers, rebounders, etc.)
* **Player search** with instant statistical analysis
* **Available players** ranked by Z-scores for waiver wire targets
* **Statistical breakdowns** showing strengths and weaknesses

### 🌐 Web UI

* **FastAPI backend** with 30+ endpoints (Swagger UI at `/docs`)
* **React frontend** with responsive design
* **Yahoo OAuth integration** for secure league access
* **Real-time data** from Yahoo Fantasy Sports API

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python 3.11) with async HTTP
* **Frontend:** React 18 + Vite + TailwindCSS
* **Database:** PostgreSQL 15 (SQLAlchemy ORM)
* **Cache:** Redis 7 + Celery for background tasks
* **Analytics:** pandas, numpy, scikit-learn for Z-score calculations
* **Deployment:** Docker Compose with 5 services

## 📦 Quick Start

### Prerequisites
- Docker & Docker Compose
- Yahoo Developer Account
- Active Yahoo Fantasy Basketball league

### 1. Clone the Repository

```bash
git clone https://github.com/jshabun/oracle.git
cd oracle
```

### 2. Set Up Yahoo API Credentials

Follow the detailed guide in `docs/YAHOO_OAUTH_SETUP.md` or quick start:

1. Create app at [Yahoo Developer Network](https://developer.yahoo.com/apps/)
2. Set redirect URI to: `http://localhost:8000/api/v1/yahoo/callback`
3. Copy credentials to `backend/.env`:

```bash
# Yahoo API Credentials
YAHOO_CLIENT_ID=your-client-id-here
YAHOO_CLIENT_SECRET=your-client-secret-here

# These will be populated after OAuth flow
YAHOO_ACCESS_TOKEN=
YAHOO_REFRESH_TOKEN=
```

### 3. Authenticate with Yahoo

```bash
# Run OAuth test script
python test_oauth.py
```

This will:
1. Open your browser to Yahoo login
2. Authenticate and authorize the app
3. Save tokens to `backend/.env`

### 4. Run with Docker

```bash
# Start all services
docker-compose up --build

# Or use quick start script
./start.sh
```

Services will be available at:
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000

### 5. Test the Integration

```bash
# Run test suite
python test_data_integration.py
```

This validates:
- ✅ Data mapper parsing Yahoo responses
- ✅ Yahoo API connection and authentication
- ✅ Player data service methods
- ✅ Analytics engine Z-score calculations

## 📖 Documentation

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Comprehensive setup and usage
- **[API Endpoints Reference](docs/ENDPOINTS_GUIDE.md)** - How to use each endpoint
- **[Yahoo OAuth Setup](docs/YAHOO_OAUTH_SETUP.md)** - Detailed authentication guide
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Common commands and workflows
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components

## 🎯 Usage Examples

### Get Draft Recommendations

```bash
# Start a draft session
curl -X POST "http://localhost:8000/api/v1/draft/start?league_key=nba.l.12345&draft_position=3"

# Get recommendations
curl "http://localhost:8000/api/v1/draft/recommendations?session_id=<session-id>&limit=10"
```

### Search Players

```bash
curl "http://localhost:8000/api/v1/players/search?league_key=nba.l.12345&query=LeBron"
```

### Get Category Rankings

```bash
# Top point scorers
curl "http://localhost:8000/api/v1/players/rankings/category/PTS?league_key=nba.l.12345&limit=20"

# Top rebounders
curl "http://localhost:8000/api/v1/players/rankings/category/REB?league_key=nba.l.12345&limit=20"
```

See `docs/ENDPOINTS_GUIDE.md` for complete API documentation.

## 📊 How It Works

### Z-Score Analysis

The app uses **statistical Z-scores** to evaluate players across all 9 categories:

1. **Calculate league averages** for each category
2. **Compute standard deviations** to measure variance
3. **Generate Z-scores** showing how many standard deviations from average
4. **Sum Z-scores** for total fantasy value

**Example:** A player with Z-scores of (FG%: 1.2, FT%: 0.8, 3PM: 0.3, PTS: 2.1, REB: 2.5, AST: 1.8, STL: 0.5, BLK: 0.3, TO: -0.5) has a **total value of 8.8** — elite!

### Punt Strategy Detection

The draft engine automatically detects which categories you're "punting" (ignoring) based on your roster:

- If 3+ players are weak in a category (Z-score < -0.5), it's flagged as punted
- Recommendations then prioritize players strong in your non-punted categories
- Common punts: FG% (draft high-volume shooters), TO (draft ball-handlers)

## 📋 Development Roadmap

* [x] Project structure and Docker setup
* [x] Yahoo Fantasy Sports OAuth 2.0 integration
* [x] 9-category Z-score analytics engine
* [x] Data integration layer (Yahoo API → Analytics)
* [x] Draft mode with real-time recommendations
* [x] Player search and rankings endpoints
* [ ] Database models for persistence
* [ ] Frontend API integration and UI polish
* [ ] Waiver wire optimizer
* [ ] Trade analyzer with category impact
* [ ] Lineup optimizer (daily/weekly)
* [ ] Advanced punt strategy customization

## 🔧 Architecture

```
oracle/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # REST API endpoints
│   │   ├── core/        # Analytics engine, config
│   │   ├── models/      # Database models (TODO)
│   │   └── services/    # Yahoo API, data mapping
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page views
│   │   └── services/    # API client (TODO)
│   ├── Dockerfile
│   └── package.json
├── docs/                # Documentation
├── docker-compose.yml   # Multi-container orchestration
└── test_*.py           # Test scripts
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with details
2. **Suggest features** - Ideas for improvements
3. **Submit PRs** - Bug fixes or new features
4. **Improve docs** - Help others get started

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

## 🙌 Acknowledgments

* [Yahoo Fantasy Sports API](https://developer.yahoo.com/fantasysports/guide/) - Player data and league integration
* Fantasy basketball community for strategy insights
* Z-score methodology from sabermetrics and fantasy analytics

---

### ⭐ If this project helps your fantasy season, give it a star on GitHub!

**Questions?** Check the [docs](docs/) or open an issue.
