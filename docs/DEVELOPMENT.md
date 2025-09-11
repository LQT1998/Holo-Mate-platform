# Holo-Mate Development Guide

## 🎯 Quick Start

### 1. Setup Development Environment
```bash
# Run the setup script
./scripts/setup-dev.sh

# Or manually:
# 1. Copy environment variables
cp env.example .env

# 2. Start services
docker-compose up -d

# 3. Setup Python environment
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Setup frontend
cd frontend/web_app
npm install
npm run dev
```

### 2. Follow Task List
The complete development task list is in `docs/tasks.md` with 136 detailed tasks organized by phases:

- **Phase 3.1**: Setup (T001-T013)
- **Phase 3.2**: Tests First - TDD (T014-T046) 
- **Phase 3.3**: Core Implementation (T047-T106)
- **Phase 3.4**: Integration (T107-T119)
- **Phase 3.5**: Polish (T120-T131)
- **Phase 3.6**: Release & Versioning (T132-T136)

## 🏗️ Project Structure

```
holo-mate-platform/
├── backend/                 # Python FastAPI services
│   ├── auth_service/        # Authentication & user management
│   ├── ai_service/          # AI companion & conversation
│   ├── streaming_service/   # Real-time voice processing
│   └── shared/              # Common models & utilities
├── frontend/                # Frontend applications
│   ├── web_app/            # Next.js dashboard
│   └── mobile_app/         # React Native mobile app
├── unity_client/           # Unity 3D hologram client
├── infrastructure/         # Terraform & deployment
├── docs/                   # Documentation
├── tests/                  # Test suites
└── scripts/                # Development scripts
```

## 🔧 Development Workflow

### 1. Task-Driven Development
- Follow the task list in `docs/tasks.md`
- Each task has a specific file path and requirements
- Mark tasks as complete when finished
- Use TDD approach: Tests → Implementation → Refactor

### 2. Parallel Development
Tasks marked with `[P]` can be developed in parallel:
- Different files = parallel execution
- Same file = sequential execution
- Follow dependency order

### 3. Testing Strategy
- **Contract Tests**: API endpoint validation
- **Integration Tests**: User story validation
- **Unit Tests**: Component testing
- **E2E Tests**: Full user journey testing

## 🚀 Getting Started with Tasks

### Phase 3.1: Setup (Start Here)
```bash
# T001: Create project structure ✓ (Already done)
# T002: Initialize Python FastAPI backend services
cd backend/auth_service
# Add your implementation here

# T003: Initialize Next.js web application  
cd frontend/web_app
# Add your implementation here

# T004: Initialize React Native mobile application
cd frontend/mobile_app
# Add your implementation here
```

### Phase 3.2: Tests First (TDD)
```bash
# T014: Contract test POST /auth/login
mkdir -p tests/contract
touch tests/contract/test_auth_login.py
# Write failing test first

# T015: Contract test POST /auth/refresh
touch tests/contract/test_auth_refresh.py
# Write failing test first
```

### Phase 3.3: Core Implementation
```bash
# T047: User model
touch backend/shared/src/models/user.py
# Implement User model

# T048: AICompanion model
touch backend/shared/src/models/ai_companion.py
# Implement AICompanion model
```

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend/web_app
npm test

cd frontend/mobile_app
npm test
```

### All Tests
```bash
# Run all tests
./scripts/run-tests.sh
```

## 🔍 Code Quality

### Python
```bash
cd backend
black . --check
isort . --check-only
flake8 .
mypy .
```

### TypeScript/JavaScript
```bash
cd frontend/web_app
npm run lint
npm run type-check
```

## 📦 Docker Development

### Start All Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f auth_service
docker-compose logs -f ai_service
docker-compose logs -f streaming_service
```

### Stop Services
```bash
docker-compose down
```

## 🗄️ Database

### Migrations
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d postgres
# Wait for postgres to start
alembic upgrade head
```

## 🔧 Environment Variables

Copy `env.example` to `.env` and configure:

### Required API Keys
- `OPENAI_API_KEY`: OpenAI API key for LLM
- `ELEVENLABS_API_KEY`: ElevenLabs API key for TTS
- `STRIPE_SECRET_KEY`: Stripe API key for payments

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### Services
- `AUTH_SERVICE_URL`: Auth service URL
- `AI_SERVICE_URL`: AI service URL
- `STREAMING_SERVICE_URL`: Streaming service URL

## 📚 Documentation

- **API Spec**: `docs/contracts/api-spec.yaml`
- **Data Model**: `docs/data-model.md`
- **Architecture**: `docs/plan.md`
- **Tasks**: `docs/tasks.md`

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Database connection**: Check DATABASE_URL in .env
3. **API keys**: Verify all required keys are set
4. **Dependencies**: Run `pip install -r requirements.txt`

### Getting Help

- Check the task list in `docs/tasks.md`
- Review the API specification
- Check Docker logs for errors
- Follow the TDD approach

## 🎯 Next Steps

1. **Start with Phase 3.1**: Complete setup tasks
2. **Follow TDD**: Write tests before implementation
3. **Use parallel development**: Work on independent tasks simultaneously
4. **Maintain quality**: Follow coding standards and testing requirements
5. **Document progress**: Update task status as you complete them

Happy coding! 🚀
