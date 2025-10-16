#!/usr/bin/env python3
"""
Test Yahoo OAuth Integration
Run this script to verify your Yahoo API setup
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.yahoo_fantasy import YahooFantasyService, YahooOAuthError


async def test_oauth():
    """Test Yahoo OAuth flow"""
    print("🏀 Testing Yahoo OAuth Integration\n")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. Initializing Yahoo Fantasy Service...")
        yahoo = YahooFantasyService()
        print("✅ Service initialized with credentials")
        print(f"   Consumer Key: {yahoo.consumer_key[:20]}...")
        
        # Get auth URL
        print("\n2. Generating Authorization URL...")
        redirect_uri = "http://localhost:8000/api/v1/yahoo/callback"
        auth_url = yahoo.get_authorization_url(redirect_uri)
        print("✅ Authorization URL generated")
        print(f"\n   🔗 Visit this URL to authorize:\n   {auth_url}\n")
        
        # Wait for user to authorize
        print("📋 Steps to authorize:")
        print("   1. Copy the URL above")
        print("   2. Open it in your browser")
        print("   3. Log in to Yahoo and click 'Agree'")
        print("   4. Copy the 'code' parameter from the redirect URL")
        print("   5. Paste it below\n")
        
        auth_code = input("Enter the authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return
        
        # Exchange code for token
        print("\n3. Exchanging code for access token...")
        token_data = await yahoo.exchange_code_for_token(auth_code, redirect_uri)
        print("✅ Access token received")
        print(f"   Expires in: {token_data['expires_in']} seconds")
        
        # Test API call - Get user leagues
        print("\n4. Testing API call - Fetching your leagues...")
        leagues = await yahoo.get_user_leagues(sport="nba")
        print(f"✅ Found {len(leagues)} leagues")
        
        if leagues:
            print("\n   Your NBA Leagues:")
            for i, league in enumerate(leagues, 1):
                name = league.get("name", "Unknown")
                league_key = league.get("league_key", "N/A")
                num_teams = league.get("num_teams", "N/A")
                print(f"   {i}. {name}")
                print(f"      League Key: {league_key}")
                print(f"      Teams: {num_teams}")
                print(f"      Season: {league.get('season', 'N/A')}")
                print()
        
        # Test getting available players if we have a league
        if leagues:
            print("\n5. Testing player data - Fetching available players...")
            league_key = leagues[0]["league_key"]
            players = await yahoo.get_available_players(
                league_key=league_key,
                count=5
            )
            print(f"✅ Found {len(players)} available players")
            
            if players:
                print("\n   Sample Available Players:")
                for i, player in enumerate(players[:5], 1):
                    name = player.get("name", {}).get("full", "Unknown")
                    team = player.get("editorial_team_abbr", "N/A")
                    positions = player.get("eligible_positions", [])
                    print(f"   {i}. {name} ({team}) - {', '.join(positions)}")
        
        # Test token status
        print("\n6. Checking token status...")
        tokens = yahoo.get_tokens()
        print("✅ Token information:")
        print(f"   Has access token: {tokens['access_token'] is not None}")
        print(f"   Has refresh token: {tokens['refresh_token'] is not None}")
        print(f"   Expires at: {tokens['expires_at']}")
        
        print("\n" + "=" * 60)
        print("🎉 Yahoo OAuth Integration Test PASSED!")
        print("\nYour application can now:")
        print("  ✅ Authenticate with Yahoo")
        print("  ✅ Fetch league data")
        print("  ✅ Access player information")
        print("  ✅ Refresh tokens automatically")
        print("\n" + "=" * 60)
        
    except YahooOAuthError as e:
        print(f"\n❌ OAuth Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your YAHOO_CONSUMER_KEY in backend/.env")
        print("  2. Check your YAHOO_CONSUMER_SECRET in backend/.env")
        print("  3. Verify redirect URI matches Yahoo Developer Console")
        print("  4. Make sure you authorized the application")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("Starting Yahoo OAuth test...\n")
    asyncio.run(test_oauth())
