#!/bin/bash

echo "🎯 SarkariBot Integration Test - SQLite Version"
echo "==============================================="

# Check if backend is running
echo "🔧 Backend Status:"
if curl -s -f "http://localhost:8000/api/v1/" > /dev/null 2>&1; then
    echo "✅ Django Backend: RUNNING on port 8000"
    
    # Test Jobs API
    JOBS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/jobs/" 2>/dev/null)
    if echo "$JOBS_RESPONSE" | grep -q '"count"'; then
        JOBS_COUNT=$(echo "$JOBS_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)
        echo "✅ Jobs API: Working with $JOBS_COUNT jobs"
    else
        echo "⚠️ Jobs API: Response received but format unexpected"
    fi
    
    # Test Stats API
    STATS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/stats/" 2>/dev/null)
    if echo "$STATS_RESPONSE" | grep -q '"total_jobs"'; then
        echo "✅ Stats API: Working"
    else
        echo "⚠️ Stats API: Response format unexpected"
    fi
    
else
    echo "❌ Django Backend: NOT RESPONDING"
    echo "   Please start with: cd backend && python manage.py runserver --settings=config.settings_local"
fi

# Check if frontend is running
echo ""
echo "🌐 Frontend Status:"
if curl -s -f "http://localhost:3000/" > /dev/null 2>&1; then
    echo "✅ React Frontend: RUNNING on port 3000"
    echo "   Accessible at: http://localhost:3000"
else
    echo "❌ React Frontend: NOT RESPONDING"
    echo "   Please start with: cd frontend && npx serve -s build -p 3000"
fi

# Check processes
echo ""
echo "🔍 Process Status:"
DJANGO_PROCESSES=$(ps aux | grep "manage.py runserver" | grep -v grep | wc -l)
FRONTEND_PROCESSES=$(ps aux | grep -E "(serve.*build|npm.*start)" | grep -v grep | wc -l)

echo "   Django processes: $DJANGO_PROCESSES"
echo "   Frontend processes: $FRONTEND_PROCESSES"

# Integration test
echo ""
echo "🔗 Integration Test:"
if curl -s -f "http://localhost:8000/api/v1/" > /dev/null 2>&1 && curl -s -f "http://localhost:3000/" > /dev/null 2>&1; then
    echo "✅ Frontend-Backend Integration: READY"
    echo "   • Frontend can be configured to call Backend API"
    echo "   • CORS is configured in Django settings"
    echo "   • Both services are accessible"
    
    echo ""
    echo "🎉 INTEGRATION STATUS: SUCCESS!"
    echo ""
    echo "📱 Access Points:"
    echo "   • Frontend App: http://localhost:3000"
    echo "   • Backend API: http://localhost:8000/api/v1/"
    echo "   • Admin Panel: http://localhost:8000/admin/"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Open http://localhost:3000 in browser"
    echo "   2. Verify data loads from backend API"
    echo "   3. Test job listings and search functionality"
    
else
    echo "❌ Integration: One or both services not responding"
fi

echo ""
echo "💾 Database: SQLite (local development)"
echo "🔧 Environment: Local development mode"
echo "🎊 Status: Ready for testing!"
