@echo off
REM Noma Card House - Setup Script for Windows
REM This script automates the installation process

echo.
echo 🎴 Noma Card House - Setup Script
echo ==================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

echo ✅ Node.js detected
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Docker is not installed. Database setup will be skipped.
    echo    Please install Docker or configure PostgreSQL manually.
    set SKIP_DOCKER=true
) else (
    echo ✅ Docker detected
    set SKIP_DOCKER=false
)

echo.
echo 📦 Installing dependencies...
call npm install

echo.
echo 📝 Setting up environment variables...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file
    echo ⚠️  Please edit .env with your configuration (Stripe keys, etc.)
) else (
    echo ⚠️  .env file already exists, skipping...
)

if "%SKIP_DOCKER%"=="false" (
    echo.
    echo 🐳 Starting PostgreSQL with Docker...
    docker-compose up -d postgres

    echo ⏳ Waiting for PostgreSQL to be ready...
    timeout /t 10 /nobreak >nul

    echo ✅ PostgreSQL is ready!

    echo.
    echo 🗄️  Setting up database schema...
    call npm run db:push

    echo.
    echo 🌱 Seeding database with sample data...
    call npm run db:seed
) else (
    echo.
    echo ⚠️  Docker not available. Please:
    echo    1. Install and configure PostgreSQL manually
    echo    2. Update DATABASE_URL in .env
    echo    3. Run: npm run db:push
    echo    4. Run: npm run db:seed
)

echo.
echo ✅ Setup complete!
echo.
echo 📚 Next steps:
echo    1. Edit .env with your Stripe API keys
echo    2. Run: npm run dev
echo    3. Open: http://localhost:3000
echo.
echo 👤 Admin credentials (from seed):
echo    Email: admin@nomacardhouse.com
echo    Password: admin123
echo.
echo 🎉 Happy coding!
pause
