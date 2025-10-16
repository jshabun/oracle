#!/usr/bin/env python3
"""
Test script for data integration layer

Tests the connection between Yahoo API, data mapper, and analytics engine
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.yahoo_fantasy import YahooFantasyService
from app.services.data_mapper import YahooDataMapper
from app.services.player_data_service import PlayerDataService
from app.core.analytics import CategoryAnalyzer, DraftEngine


async def test_data_mapper():
    """Test YahooDataMapper with sample Yahoo API response"""
    print("=" * 60)
    print("TEST 1: Data Mapper with Sample Response")
    print("=" * 60)
    
    # Sample Yahoo player response (simplified version)
    sample_player = {
        "player_id": "5479",
        "name": {
            "full": "Nikola Jokic"
        },
        "editorial_team_abbr": "Den",
        "display_position": "C",
        "player_stats": {
            "stats": [
                {"stat_id": "0", "value": "65"},  # GP
                {"stat_id": "5", "value": "520"},  # FGM
                {"stat_id": "6", "value": "953"},  # FGA
                {"stat_id": "7", "value": "298"},  # FTM
                {"stat_id": "8", "value": "352"},  # FTA
                {"stat_id": "10", "value": "193"},  # 3PM
                {"stat_id": "12", "value": "1531"},  # PTS
                {"stat_id": "15", "value": "841"},  # REB
                {"stat_id": "16", "value": "625"},  # AST
                {"stat_id": "17", "value": "86"},  # STL
                {"stat_id": "18", "value": "58"},  # BLK
                {"stat_id": "19", "value": "209"},  # TO
            ]
        }
    }
    
    mapper = YahooDataMapper()
    player_stats = mapper.parse_player_stats(sample_player)
    
    if player_stats:
        print(f"\n✅ Successfully parsed player: {player_stats.name}")
        print(f"   Team: {player_stats.team} | Position: {player_stats.position}")
        print(f"\n   Stats:")
        print(f"   FG%: {player_stats.fg_pct:.1f}% ({player_stats.fgm}/{player_stats.fga})")
        print(f"   FT%: {player_stats.ft_pct:.1f}% ({player_stats.ftm}/{player_stats.fta})")
        print(f"   3PM: {player_stats.three_pm}")
        print(f"   PTS: {player_stats.pts}")
        print(f"   REB: {player_stats.reb}")
        print(f"   AST: {player_stats.ast}")
        print(f"   STL: {player_stats.stl}")
        print(f"   BLK: {player_stats.blk}")
        print(f"   TO:  {player_stats.to}")
        
        # Test formatting for response
        formatted = mapper.format_player_for_response(player_stats)
        print(f"\n   Formatted response includes {len(formatted['stats'])} stat categories")
        
        return True
    else:
        print("❌ Failed to parse player stats")
        return False


async def test_yahoo_connection():
    """Test connection to Yahoo API"""
    print("\n" + "=" * 60)
    print("TEST 2: Yahoo API Connection")
    print("=" * 60)
    
    yahoo = YahooFantasyService()
    
    # Check if we have credentials
    if not yahoo.client_id or not yahoo.client_secret:
        print("❌ Yahoo credentials not configured in .env")
        print("   Please set YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET")
        return False
    
    print("✅ Yahoo credentials found")
    
    # Check if we have access token
    if not yahoo.access_token:
        print("⚠️  No access token found")
        print("   Run test_oauth.py first to authenticate")
        return False
    
    print("✅ Access token found")
    
    try:
        # Try to get user's leagues
        leagues = await yahoo.get_user_leagues()
        
        if leagues:
            print(f"✅ Successfully connected to Yahoo API")
            print(f"   Found {len(leagues)} leagues")
            
            for league in leagues[:3]:  # Show first 3
                print(f"\n   League: {league.get('name', 'Unknown')}")
                print(f"   Key: {league.get('league_key', 'Unknown')}")
                print(f"   Season: {league.get('season', 'Unknown')}")
            
            return leagues[0].get('league_key') if leagues else None
        else:
            print("⚠️  No leagues found for this account")
            return None
            
    except Exception as e:
        print(f"❌ Error connecting to Yahoo API: {e}")
        return None


async def test_player_data_service(league_key: str):
    """Test PlayerDataService integration"""
    print("\n" + "=" * 60)
    print("TEST 3: Player Data Service")
    print("=" * 60)
    
    yahoo = YahooFantasyService()
    service = PlayerDataService(yahoo)
    
    try:
        # Test 1: Get available players with stats
        print("\n📊 Fetching available players...")
        players = await service.get_available_players_with_stats(
            league_key=league_key,
            limit=10
        )
        
        if players:
            print(f"✅ Retrieved {len(players)} players with stats")
            print(f"\n   Sample player: {players[0].name}")
            print(f"   Team: {players[0].team} | Position: {players[0].position}")
        else:
            print("⚠️  No players returned")
            return False
        
        # Test 2: Get draft recommendations
        print("\n🎯 Getting draft recommendations...")
        recommendations = await service.get_draft_recommendations(
            league_key=league_key,
            current_roster=[],
            limit=5
        )
        
        if recommendations:
            print(f"✅ Generated {len(recommendations)} recommendations")
            print("\n   Top 5 recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n   {i}. {rec['name']} ({rec['team']}) - {rec['position']}")
                print(f"      Total Value: {rec['total_value']:.2f}")
                print(f"      Rank: #{rec['rank']}")
                
                # Show top categories
                z_scores = rec.get('z_scores', {})
                if z_scores:
                    top_cats = sorted(
                        [(cat, val) for cat, val in z_scores.items() if cat != 'total_z'],
                        key=lambda x: x[1],
                        reverse=True
                    )[:3]
                    print(f"      Best at: {', '.join(f'{cat} ({val:.2f})' for cat, val in top_cats)}")
        else:
            print("⚠️  No recommendations generated")
            return False
        
        # Test 3: Search players
        print("\n🔍 Testing player search...")
        search_results = await service.search_players(
            league_key=league_key,
            query="LeBron",
            limit=3
        )
        
        if search_results:
            print(f"✅ Found {len(search_results)} players matching 'LeBron'")
            for player in search_results:
                print(f"   - {player['name']} ({player['team']})")
        else:
            print("⚠️  No search results")
        
        # Test 4: Category rankings
        print("\n📈 Testing category rankings...")
        rankings = await service.get_player_rankings(
            league_key=league_key,
            category="PTS",
            limit=5
        )
        
        if rankings:
            print(f"✅ Top 5 in PTS:")
            for i, player in enumerate(rankings, 1):
                pts = player.get('stats', {}).get('PTS', 0)
                z_score = player.get('z_scores', {}).get('PTS', 0)
                print(f"   {i}. {player['name']}: {pts} PTS (Z: {z_score:.2f})")
        else:
            print("⚠️  No rankings generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in player data service: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_analytics_engine():
    """Test analytics engine with sample data"""
    print("\n" + "=" * 60)
    print("TEST 4: Analytics Engine")
    print("=" * 60)
    
    from app.core.analytics import PlayerStats
    
    # Create sample players
    players = [
        PlayerStats(
            player_id="1", name="High Volume Scorer", team="LAL", position="SG",
            fgm=500, fga=1000, ftm=400, fta=500, three_pm=200,
            pts=1600, reb=300, ast=400, stl=80, blk=20, to=150
        ),
        PlayerStats(
            player_id="2", name="Efficient Big", team="DEN", position="C",
            fgm=400, fga=600, ftm=200, fta=250, three_pm=0,
            pts=1000, reb=800, ast=200, stl=50, blk=150, to=100
        ),
        PlayerStats(
            player_id="3", name="Point Guard", team="GSW", position="PG",
            fgm=300, fga=700, ftm=150, fta=170, three_pm=180,
            pts=930, reb=200, ast=600, stl=100, blk=10, to=120
        ),
    ]
    
    # Calculate Z-scores
    analyzer = CategoryAnalyzer()
    z_scores = analyzer.calculate_z_scores(players)
    
    print("\n📊 Z-Score Analysis:")
    print(z_scores[['name', 'FG%_z', 'FT%_z', '3PM_z', 'PTS_z', 'total_z']].to_string(index=False))
    
    # Test draft engine
    engine = DraftEngine(analyzer)
    recommendations = engine.get_draft_recommendations(
        available_players=players,
        current_roster=[],
        punt_categories=[]
    )
    
    print(f"\n🎯 Draft Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['name']} - Total Z: {rec['total_value']:.2f}")
    
    return True


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FANTASY BASKETBALL DATA INTEGRATION TEST SUITE")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Data Mapper (no API calls needed)
    results['mapper'] = await test_data_mapper()
    
    # Test 2: Yahoo Connection
    league_key = await test_yahoo_connection()
    results['yahoo'] = league_key is not None
    
    # Test 3: Player Data Service (requires Yahoo connection)
    if league_key:
        results['service'] = await test_player_data_service(league_key)
    else:
        print("\n⏭️  Skipping Player Data Service test (no league key)")
        results['service'] = None
    
    # Test 4: Analytics Engine (no API calls needed)
    results['analytics'] = await test_analytics_engine()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        
        print(f"{test_name.upper():20s}: {status}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])
    
    print("\n" + "=" * 60)
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
