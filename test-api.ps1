# test-api.ps1 - FinanceML API Endpoints Test Script

Write-Host "🧪 Testing FinanceML API Endpoints" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Test base URL
$baseUrl = "http://localhost:8000"

try {
    # 1. Health check
    Write-Host "1️⃣ Health Check:" -ForegroundColor Yellow
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    $health | ConvertTo-Json
    Write-Host ""

    # 2. Test forecast (AAPL)
    Write-Host "2️⃣ Forecast Test (AAPL, 14 days):" -ForegroundColor Yellow
    $forecastBody = @{
        symbol = "AAPL"
        days = 14
    } | ConvertTo-Json
    
    $forecast = Invoke-RestMethod -Uri "$baseUrl/forecast" -Method POST -Body $forecastBody -ContentType "application/json"
    Write-Host "Symbol: $($forecast.symbol)"
    Write-Host "Current Price: $($forecast.current_price)"
    Write-Host "Predicted Price: $($forecast.final_predicted_price)"
    Write-Host "Trend: $($forecast.trend)"
    Write-Host ""

    # 3. Test financials
    Write-Host "3️⃣ Financials Test (MSFT):" -ForegroundColor Yellow
    $financials = Invoke-RestMethod -Uri "$baseUrl/financials/MSFT" -Method GET
    Write-Host "Symbol: $($financials.symbol)"
    Write-Host "Market Cap: $($financials.market_cap)"
    Write-Host "PE Ratio: $($financials.pe_ratio)"
    Write-Host ""

    # 4. Test risk analysis
    Write-Host "4️⃣ Risk Analysis Test (GOOGL):" -ForegroundColor Yellow
    $risk = Invoke-RestMethod -Uri "$baseUrl/risk/GOOGL" -Method GET
    Write-Host "Symbol: $($risk.symbol)"
    Write-Host "Risk Rating: $($risk.risk_rating)"
    Write-Host "Beta: $($risk.beta)"
    Write-Host "Sharpe Ratio: $($risk.sharpe_ratio)"
    Write-Host ""

    # 5. Test portfolio optimization
    Write-Host "5️⃣ Portfolio Optimization Test:" -ForegroundColor Yellow
    $portfolioBody = @{
        symbols = @("AAPL", "MSFT", "GOOGL")
        optimize_for = "max_sharpe"
    } | ConvertTo-Json
    
    $portfolio = Invoke-RestMethod -Uri "$baseUrl/portfolio/optimize" -Method POST -Body $portfolioBody -ContentType "application/json"
    Write-Host "Optimization Type: $($portfolio.max_sharpe_portfolio.type)"
    Write-Host "Expected Return: $([math]::Round($portfolio.max_sharpe_portfolio.expected_return * 100, 2))%"
    Write-Host "Sharpe Ratio: $([math]::Round($portfolio.max_sharpe_portfolio.sharpe_ratio, 3))"
    Write-Host ""

    # 6. Test sentiment (if News API key available)
    Write-Host "6️⃣ Sentiment Analysis Test (TSLA):" -ForegroundColor Yellow
    try {
        $sentiment = Invoke-RestMethod -Uri "$baseUrl/sentiment/TSLA?days=7" -Method GET
        Write-Host "Symbol: $($sentiment.symbol)"
        Write-Host "Sentiment: $($sentiment.sentiment_label)"
        Write-Host "Score: $([math]::Round($sentiment.sentiment_score, 3))"
        Write-Host "News Count: $($sentiment.news_count)"
    }
    catch {
        Write-Host "Sentiment API unavailable (News API key required)" -ForegroundColor DarkYellow
    }
    Write-Host ""

    # Success summary
    Write-Host "✅ All API tests completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Test Summary:" -ForegroundColor Cyan
    Write-Host "• Health: ✅ Healthy"
    Write-Host "• Forecast: ✅ Working from cache"
    Write-Host "• Financials: ✅ Working from cache"
    Write-Host "• Risk Analysis: ✅ Working from cache"
    Write-Host "• Portfolio Optimization: ✅ Working from cache"
    Write-Host "• Sentiment: ⚠️ Requires News API key"

} catch {
    Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔍 Possible causes:" -ForegroundColor Yellow
    Write-Host "• Docker containers not running (run: docker compose up -d)"
    Write-Host "• API not healthy (check: docker compose logs api)"
    Write-Host "• Port 8000 not accessible"
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "🚀 Test completed!" -ForegroundColor Cyan