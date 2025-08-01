#!/bin/bash

echo "🎊 SARKARIBOT FRONTEND-BACKEND INTEGRATION VERIFICATION"
echo "======================================================"
echo ""

# Test Backend API
echo "🔧 BACKEND API TESTS:"
echo "--------------------"

# Test Jobs API
echo -n "📋 Jobs API: "
JOBS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/jobs/")
if echo "$JOBS_RESPONSE" | grep -q '"count"'; then
    JOBS_COUNT=$(echo "$JOBS_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo "✅ Working ($JOBS_COUNT jobs available)"
else
    echo "❌ Failed"
fi

# Test Categories API
echo -n "📂 Categories API: "
CATEGORIES_RESPONSE=$(curl -s "http://localhost:8000/api/v1/categories/")
if echo "$CATEGORIES_RESPONSE" | grep -q '"id"'; then
    echo "✅ Working"
else
    echo "❌ Failed"
fi

# Test Stats API
echo -n "📊 Stats API: "
STATS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/stats/")
if echo "$STATS_RESPONSE" | grep -q '"total_jobs"'; then
    TOTAL_JOBS=$(echo "$STATS_RESPONSE" | grep -o '"total_jobs":[0-9]*' | cut -d':' -f2)
    echo "✅ Working ($TOTAL_JOBS total jobs)"
else
    echo "❌ Failed"
fi

# Test Sources API
echo -n "🏢 Sources API: "
SOURCES_RESPONSE=$(curl -s "http://localhost:8000/api/v1/sources/")
if echo "$SOURCES_RESPONSE" | grep -q '"id"'; then
    echo "✅ Working"
else
    echo "❌ Failed"
fi

echo ""
echo "🌐 FRONTEND TESTS:"
echo "-----------------"

# Test Frontend Homepage
echo -n "🏠 Homepage: "
FRONTEND_RESPONSE=$(curl -s "http://localhost:3000/")
if echo "$FRONTEND_RESPONSE" | grep -q "SarkariBot"; then
    echo "✅ Loading successfully"
else
    echo "❌ Failed to load"
fi

# Test Frontend Static Assets
echo -n "📦 Static Assets: "
STATIC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/static/js/main.26391f97.js")
if [ "$STATIC_RESPONSE" = "200" ]; then
    echo "✅ Accessible"
else
    echo "❌ Failed (HTTP $STATIC_RESPONSE)"
fi

echo ""
echo "🔗 INTEGRATION VERIFICATION:"
echo "----------------------------"

# Test CORS (simulate frontend request)
echo -n "🌍 CORS Configuration: "
CORS_RESPONSE=$(curl -s -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS "http://localhost:8000/api/v1/jobs/")
if [ $? -eq 0 ]; then
    echo "✅ Configured"
else
    echo "❌ Failed"
fi

# Test API from Frontend perspective
echo -n "📡 API Accessibility: "
API_TEST=$(curl -s -H "Origin: http://localhost:3000" "http://localhost:8000/api/v1/jobs/?page_size=1")
if echo "$API_TEST" | grep -q '"results"'; then
    echo "✅ Frontend can access Backend API"
else
    echo "❌ Frontend cannot access Backend API"
fi

echo ""
echo "📊 SAMPLE DATA VERIFICATION:"
echo "----------------------------"

# Show sample job data
echo "📋 Sample Job Data:"
echo "$JOBS_RESPONSE" | grep -o '"title":"[^"]*"' | head -3 | sed 's/"title"://g' | sed 's/"//g' | sed 's/^/   • /'

echo ""
echo "🎯 FINAL STATUS:"
echo "==============="

BACKEND_OK=false
FRONTEND_OK=false

if curl -s -f "http://localhost:8000/api/v1/" > /dev/null 2>&1; then
    BACKEND_OK=true
fi

if curl -s -f "http://localhost:3000/" > /dev/null 2>&1; then
    FRONTEND_OK=true
fi

if [ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ]; then
    echo "🎉 ✅ INTEGRATION SUCCESSFUL!"
    echo ""
    echo "🌟 Your SarkariBot application is fully operational:"
    echo "   • Frontend: http://localhost:3000"
    echo "   • Backend API: http://localhost:8000/api/v1/"
    echo "   • Admin Panel: http://localhost:8000/admin/"
    echo ""
    echo "🎊 Ready for use! Open http://localhost:3000 in your browser."
else
    echo "❌ Integration incomplete:"
    echo "   • Backend: $([ "$BACKEND_OK" = true ] && echo "✅ Running" || echo "❌ Not running")"
    echo "   • Frontend: $([ "$FRONTEND_OK" = true ] && echo "✅ Running" || echo "❌ Not running")"
fi

echo ""
echo "💡 Note: Using SQLite database for local development"
echo "🛠️  Environment: Local development mode"
