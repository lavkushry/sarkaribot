@echo off
REM SarkariBot Development Helper Script for Windows
REM This script provides convenient commands for Docker-based development

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Colors (if supported)
set "COLOR_INFO=echo [INFO]"
set "COLOR_SUCCESS=echo [SUCCESS]"
set "COLOR_WARNING=echo [WARNING]"
set "COLOR_ERROR=echo [ERROR]"

goto :main

:check_docker
docker --version >nul 2>&1
if errorlevel 1 (
    %COLOR_ERROR% Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    %COLOR_ERROR% Docker is not running. Please start Docker Desktop first.
    exit /b 1
)
goto :eof

:show_help
echo SarkariBot Development Helper Script for Windows
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   start         Start all development services
echo   stop          Stop all services
echo   restart       Restart all services
echo   build         Build all Docker images
echo   logs          Show logs from all services
echo   logs-backend  Show backend logs only
echo   logs-frontend Show frontend logs only
echo   logs-celery   Show Celery worker logs
echo   shell-backend Open backend shell
echo   shell-db      Open database shell
echo   test-backend  Run backend tests
echo   test-frontend Run frontend tests
echo   migrate       Run database migrations
echo   collectstatic Collect static files
echo   createsuperuser Create Django superuser
echo   clean         Clean up Docker resources
echo   status        Show status of all services
echo   urls          Show access URLs
echo   pgadmin       Start with PgAdmin
echo   help          Show this help message
echo.
goto :eof

:start_services
%COLOR_INFO% Starting SarkariBot development environment...
cd /d "%PROJECT_ROOT%"
call :check_docker
if errorlevel 1 exit /b 1
docker compose -f docker-compose.dev.yml up -d
if errorlevel 1 (
    %COLOR_ERROR% Failed to start services!
    exit /b 1
)
%COLOR_SUCCESS% All services started!
call :show_urls
goto :eof

:start_with_pgadmin
%COLOR_INFO% Starting SarkariBot development environment with PgAdmin...
cd /d "%PROJECT_ROOT%"
call :check_docker
if errorlevel 1 exit /b 1
docker compose -f docker-compose.dev.yml --profile tools up -d
if errorlevel 1 (
    %COLOR_ERROR% Failed to start services!
    exit /b 1
)
%COLOR_SUCCESS% All services started with PgAdmin!
call :show_urls
echo.
%COLOR_INFO% PgAdmin is available at: http://localhost:8080
%COLOR_INFO%   Username: admin@sarkaribot.local
%COLOR_INFO%   Password: admin123
goto :eof

:stop_services
%COLOR_INFO% Stopping all services...
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml down
%COLOR_SUCCESS% All services stopped!
goto :eof

:restart_services
%COLOR_INFO% Restarting all services...
call :stop_services
call :start_services
goto :eof

:build_images
%COLOR_INFO% Building Docker images...
cd /d "%PROJECT_ROOT%"
call :check_docker
if errorlevel 1 exit /b 1
docker compose -f docker-compose.dev.yml build
if errorlevel 1 (
    %COLOR_ERROR% Failed to build images!
    exit /b 1
)
%COLOR_SUCCESS% All images built successfully!
goto :eof

:show_logs
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml logs -f
goto :eof

:show_backend_logs
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml logs -f backend
goto :eof

:show_frontend_logs
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml logs -f frontend
goto :eof

:show_celery_logs
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml logs -f celery_worker celery_beat
goto :eof

:backend_shell
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml exec backend python manage.py shell
goto :eof

:db_shell
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml exec db psql -U postgres -d sarkaribot_dev
goto :eof

:run_backend_tests
%COLOR_INFO% Running backend tests...
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml exec backend python manage.py test
goto :eof

:run_frontend_tests
%COLOR_INFO% Running frontend tests...
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml exec frontend npm test -- --coverage --watchAll=false
goto :eof

:run_migrations
%COLOR_INFO% Running database migrations...
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate
%COLOR_SUCCESS% Migrations completed!
goto :eof

:collect_static
%COLOR_INFO% Collecting static files...
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --noinput
%COLOR_SUCCESS% Static files collected!
goto :eof

:create_superuser
%COLOR_INFO% Creating Django superuser...
cd /d "%PROJECT_ROOT%"
docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
goto :eof

:clean_docker
%COLOR_WARNING% This will remove all stopped containers, unused networks, images, and build cache.
set /p confirm="Are you sure? (y/N): "
if /i "!confirm!"=="y" (
    %COLOR_INFO% Cleaning Docker resources...
    docker system prune -f
    docker volume prune -f
    %COLOR_SUCCESS% Docker cleanup completed!
) else (
    %COLOR_INFO% Cleanup cancelled.
)
goto :eof

:show_status
cd /d "%PROJECT_ROOT%"
echo Service Status:
docker compose -f docker-compose.dev.yml ps
goto :eof

:show_urls
echo.
%COLOR_SUCCESS% Development environment is ready!
echo.
echo Frontend:     http://localhost:3000
echo Backend API:  http://localhost:8000/api/v1/
echo Admin Panel:  http://localhost:8000/admin/
echo API Docs:     http://localhost:8000/api/docs/
echo.
echo Database:
echo   PostgreSQL:   localhost:5432
echo   Redis:        localhost:6379
echo.
echo Useful commands:
echo   View logs:    dev.bat logs
echo   Backend shell: dev.bat shell-backend
echo   Run tests:    dev.bat test-backend
echo.
goto :eof

:main
if "%1"=="" goto show_help
if "%1"=="help" goto show_help
if "%1"=="start" goto start_services
if "%1"=="stop" goto stop_services
if "%1"=="restart" goto restart_services
if "%1"=="build" goto build_images
if "%1"=="logs" goto show_logs
if "%1"=="logs-backend" goto show_backend_logs
if "%1"=="logs-frontend" goto show_frontend_logs
if "%1"=="logs-celery" goto show_celery_logs
if "%1"=="shell-backend" goto backend_shell
if "%1"=="shell-db" goto db_shell
if "%1"=="test-backend" goto run_backend_tests
if "%1"=="test-frontend" goto run_frontend_tests
if "%1"=="migrate" goto run_migrations
if "%1"=="collectstatic" goto collect_static
if "%1"=="createsuperuser" goto create_superuser
if "%1"=="clean" goto clean_docker
if "%1"=="status" goto show_status
if "%1"=="urls" goto show_urls
if "%1"=="pgadmin" goto start_with_pgadmin

echo Unknown command: %1
echo.
goto show_help