#!/bin/bash

# Holo-Mate Development Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Holo-Mate development environment..."

# Check if required tools are installed
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    else
        echo "✅ $1 is installed"
    fi
}

echo "📋 Checking prerequisites..."
check_command "python3"
check_command "node"
check_command "npm"
check_command "docker"
check_command "docker-compose"

# Create virtual environment for backend
echo "🐍 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend/web_app
npm install
cd ../mobile_app
npm install
cd ../..

# Setup environment variables
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "📝 Created .env file from template. Please update with your API keys."
else
    echo "✅ .env file already exists"
fi

# Initialize git repository
echo "📁 Initializing git repository..."
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit: Holo-Mate platform setup"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Create database initialization script
echo "🗄️ Creating database initialization script..."
cat > scripts/init-db.sql << EOF
-- Holo-Mate Database Initialization
CREATE DATABASE holo_mate;
CREATE USER holo_mate WITH PASSWORD 'holo_mate_dev';
GRANT ALL PRIVILEGES ON DATABASE holo_mate TO holo_mate;
EOF

echo "✅ Database initialization script created"

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo "🎉 Setup complete! Next steps:"
echo ""
echo "1. Update .env file with your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - ELEVENLABS_API_KEY"
echo "   - STRIPE_SECRET_KEY"
echo ""
echo "2. Start the development environment:"
echo "   docker-compose up -d"
echo ""
echo "3. Run database migrations:"
echo "   cd backend && alembic upgrade head"
echo ""
echo "4. Start frontend development servers:"
echo "   cd frontend/web_app && npm run dev"
echo "   cd frontend/mobile_app && npm start"
echo ""
echo "5. Follow the task list in docs/tasks.md"
echo ""
echo "Happy coding! 🚀"
