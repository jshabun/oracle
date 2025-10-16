# Yahoo OAuth - Quick Start ⚡

Get your Fantasy Basketball Oracle connected to Yahoo in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Yahoo account
- Web browser

---

## Step 1: Get Yahoo Credentials (3 minutes)

1. **Visit**: https://developer.yahoo.com/apps/
2. **Click**: "Create an App"
3. **Fill in**:
   - Name: `Fantasy Basketball Oracle`
   - Redirect URI: `http://localhost:8000/api/v1/yahoo/callback`
   - Permissions: ✅ Fantasy Sports (Read)
4. **Save** your Client ID and Client Secret

---

## Step 2: Configure (1 minute)

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit and add your credentials
nano backend/.env
```

Add:
```env
YAHOO_CONSUMER_KEY=your_client_id_here
YAHOO_CONSUMER_SECRET=your_client_secret_here
```

---

## Step 3: Start Application (1 minute)

```bash
docker-compose up --build
```

Wait for startup (~2 minutes first time).

---

## Step 4: Authorize (2 minutes)

### Option A: Using Swagger UI

1. **Open**: http://localhost:8000/docs
2. **Find**: `/api/v1/yahoo/auth/url`
3. **Click**: "Try it out" → "Execute"
4. **Copy**: The `auth_url` from response
5. **Visit**: That URL in your browser
6. **Click**: "Agree" to authorize
7. **Done!** You'll see a success message

### Option B: Using Test Script

```bash
# Run the test script
python test_oauth.py

# Follow the prompts
# It will test everything automatically
```

---

## Step 5: Verify (1 minute)

Test that it works:

```bash
# Get your leagues
curl http://localhost:8000/api/v1/yahoo/leagues

# Should see your league data!
```

Or visit http://localhost:8000/docs and try any endpoint.

---

## What You Can Do Now ✅

With OAuth connected, you can:

- ✅ Fetch your league settings
- ✅ Get team rosters  
- ✅ Access available players
- ✅ View standings and matchups
- ✅ Search for any player
- ✅ Get player statistics

---

## Troubleshooting

### "Yahoo API credentials not configured"
→ Check `backend/.env` has your credentials

### "Authorization failed"
→ Make sure redirect URI exactly matches:
   `http://localhost:8000/api/v1/yahoo/callback`

### "Token expired"
→ Re-authorize or use:
   `curl -X POST http://localhost:8000/api/v1/yahoo/tokens/refresh`

---

## Next Steps

Now connect this to your analytics engine!

See: **`docs/DATA_INTEGRATION.md`**

---

## Full Documentation

For complete details: **`docs/YAHOO_OAUTH_SETUP.md`**

---

**That's it!** You're ready to dominate your fantasy league! 🏀🏆
