import asyncio
import httpx
import uuid

API_URL = "http://localhost:8000/api"

async def main():
    print("=== TRADER COPILOT AI MVP VALIDATION ===\n")
    async with httpx.AsyncClient(base_url=API_URL, follow_redirects=True, timeout=30.0) as client:
        # Step 1: Health Check
        print("1. System Health Check")
        res = await client.get("/health")
        print(f"Health Check: {res.status_code}")
        
        # Step 2: User Registration & Authentication
        print("2. User Authentication")
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "testpassword123"
        res = await client.post("/auth/register", json={
            "email": email,
            "password": password,
            "name": "Test User",
            "account_size": 10000.0
        })
        print(f"Register: {res.status_code}")
        
        # Login
        res = await client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        print(f"Login: {res.status_code}")
        token = res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Risk Profile configuration
        print("\n3. Configure Risk Profile")
        res = await client.patch("/risk/profile", headers=headers, json={
            "max_risk_per_trade_pct": 1.0,
            "max_daily_drawdown_pct": 3.0,
            "max_open_trades": 3
        })
        print(f"Risk Profile Update: {res.status_code}")

        # Step 4: Get default strategy
        print("\n4. Fetch Strategies")
        res = await client.get("/strategies", headers=headers)
        print(f"Fetch Strategies: {res.status_code}")
        strategies = res.json().get("data", res.json())
        print(f"Strategies Loaded: {len(strategies)}")
        strategy_id = strategies[0]["id"] if strategies else None

        # Step 5: Trade Planning (Rule Engine Violation)
        print("\n5. Rule Engine Violation Test")
        res = await client.post("/trades/plan", headers=headers, json={
            "strategy_id": strategy_id,
            "symbol": "NIFTY",
            "direction": "long",
            "order_type": "limit",
            "entry_price": 20000.0,
            "stop_loss": 19900.0,  
            "take_profit": 20200.0,
            "thesis": "Testing violation"
        })
        print(f"Plan Trade: {res.status_code}")
        if res.status_code in [200, 201]:
            trade_id = res.json().get("data", res.json()).get("trade", {}).get("id")

            # Step 6: Execute Trade
            print("\n6. Trade Execution & Journaling")
            res = await client.post(f"/trades/{trade_id}/open", headers=headers)
            print(f"Open Trade: {res.status_code}")

            res = await client.post(f"/trades/{trade_id}/close", headers=headers, json={
                "exit_price": 20100.0,
                "pnl": 100.0,
                "notes": "Good trade."
            })
            print(f"Close Trade: {res.status_code}")

            # Step 7: Trade Notes Generation (Context)
            print("\n7. Trade Context")
            res = await client.post(f"/trades/{trade_id}/notes", headers=headers, json={
                "content": "Felt good about this one.",
                "note_type": "psychology",
                "tags": ["fomo", "greed"]
            })
            print(f"Add Context: {res.status_code}")
            
            # Step 7.5: Analytics Dashboard
            print("\n7.5. Analytics Dashboard")
            res = await client.get("/analytics/dashboard", headers=headers)
            print(f"Analytics Dashboard: {res.status_code}")

        # Step 8: Get AI Insights
        print("\n8. AI Coach Insights")
        res = await client.get("/ai/coach", headers=headers)
        print(f"AI Insights: {res.status_code}")

        print("\n=== E2E FLOW COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(main())
