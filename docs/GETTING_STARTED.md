# Getting Started Guide

## Quick Start (5 minutes)

### 1. Get Yahoo Fantasy API Credentials

1. Go to https://developer.yahoo.com/apps/
2. Click "Create an App"
3. Fill in the form:
   - **Application Name**: Fantasy Basketball Oracle
   - **Description**: AI assistant for fantasy basketball
   - **Redirect URI**: `http://localhost:8000/api/v1/yahoo/callback`
   - **API Permissions**: Check "Fantasy Sports" (Read)
4. Click "Create App"
5. Copy your **Consumer Key** and **Consumer Secret**

### 2. Get Your League ID

1. Go to your Yahoo Fantasy Basketball league
2. Look at the URL: `https://basketball.fantasysports.yahoo.com/nba/XXXXX/`
3. The `XXXXX` is your League ID

### 3. Setup Environment

```bash
# Navigate to project
cd /workspaces/oracle

# Copy environment template
cp backend/.env.example backend/.env

# Edit the file with your credentials
nano backend/.env
```

Add your credentials:
```env
YAHOO_CONSUMER_KEY=your_consumer_key_here
YAHOO_CONSUMER_SECRET=your_consumer_secret_here
YAHOO_LEAGUE_ID=your_league_id_here
```

### 4. Start the Application

```bash
# Build and start all services
docker-compose up --build
```

Wait for all services to start (about 2-3 minutes first time).

### 5. Access the App

Open your browser:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Backend**: http://localhost:8000

### 6. Connect Your Yahoo Account

1. Click "Connect Yahoo" in the app
2. Log in to Yahoo
3. Authorize the application
4. You'll be redirected back to the app

**You're ready to go!** 🎉

## Development Workflow

### Backend Development

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Format code
black app/
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database Management

```bash
# Access PostgreSQL
docker exec -it oracle-db psql -U oracle -d oracle

# View tables
\dt

# Query players
SELECT name, team, position FROM players LIMIT 10;

# Exit
\q
```

### Redis Management

```bash
# Access Redis CLI
docker exec -it oracle-redis redis-cli

# View all keys
KEYS *

# Get a value
GET draft_session:123

# Exit
exit
```

## Common Tasks

### Update Player Data

```bash
# Trigger manual update
curl -X POST http://localhost:8000/api/v1/admin/update-players
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Reset Database

```bash
# Stop all services
docker-compose down

# Remove volumes
docker volume rm oracle_postgres_data

# Restart
docker-compose up
```

### Test API Endpoints

Using the Swagger UI at http://localhost:8000/docs

Or with curl:
```bash
# Health check
curl http://localhost:8000/health

# Get player rankings
curl http://localhost:8000/api/v1/players/rankings/category?category=PTS

# Start draft session
curl -X POST "http://localhost:8000/api/v1/draft/start?draft_position=5&snake=true"
```

## Troubleshooting

### "Import could not be resolved" errors

These are normal before installing dependencies. The app will work correctly once dependencies are installed.

### Yahoo API not connecting

1. Check your Consumer Key/Secret are correct
2. Verify redirect URI matches exactly: `http://localhost:8000/api/v1/yahoo/callback`
3. Ensure "Fantasy Sports" permission is enabled
4. Try regenerating your Consumer Secret

### Database connection failed

```bash
# Check if database is running
docker ps | grep oracle-db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Frontend not connecting to backend

1. Check CORS settings in `backend/app/core/config.py`
2. Verify `VITE_API_URL` in frontend
3. Ensure backend is running on port 8000

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

## Next Steps

Now that you're set up:

1. **Test Draft Mode**: Go to Draft Mode and run a mock draft
2. **Explore Analytics**: Check player rankings and category leaders
3. **Connect Yahoo**: Authorize your Yahoo account to see real data
4. **Customize Settings**: Adjust league settings in `backend/app/core/config.py`

## Additional Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [API Reference](API.md)
- [Analytics Methodology](ANALYTICS.md)
- [Yahoo Fantasy API Docs](https://developer.yahoo.com/fantasysports/guide/)

## Getting Help

If you run into issues:

1. Check the logs: `docker-compose logs -f`
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check Yahoo API status: https://status.yahoo.com/
4. Open an issue on GitHub with:
   - Error messages
   - Relevant logs
   - Steps to reproduce

Happy drafting! 🏀
