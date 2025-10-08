#!/bin/bash
# test-forecast.sh - API forecast endpoint'ini test et

echo "🧪 Testing Forecast API"
echo "======================="
echo ""

# 1. Health check
echo "1️⃣ Health Check:"
curl -s http://localhost:8000/health | jq .
echo ""

# 2. Test valid forecast request
echo "2️⃣ Valid Forecast Request:"
curl -s -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","days":14}' | jq .
echo ""

# 3. Test with different symbol
echo "3️⃣ Different Symbol (GOOGL):"
curl -s -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GOOGL","days":7}' | jq .
echo ""

# 4. Test invalid request (missing symbol)
echo "4️⃣ Invalid Request (missing symbol):"
curl -s -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{"days":14}' | jq .
echo ""

# 5. Test invalid request (invalid days)
echo "5️⃣ Invalid Request (days > 90):"
curl -s -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","days":100}' | jq .
echo ""

# 6. Debug endpoint
echo "6️⃣ Debug Endpoint:"
curl -s -X POST http://localhost:8000/forecast/debug \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","days":14}' | jq .
echo ""

# 7. Check API logs
echo "7️⃣ Recent API Logs:"
docker-compose logs --tail=30 api

echo ""
echo "======================="
echo "✅ Test completed!"

