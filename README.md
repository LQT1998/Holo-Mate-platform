# Holo-Mate AI Companion Platform

**Next-generation AI Companion platform combining real-time voice chat with 3D hologram display**

## 🎯 Project Overview

Holo-Mate is a revolutionary AI Companion platform that enables users to interact with personalized AI companions through real-time voice chat and 3D hologram display. The system provides natural conversation experiences with realistic emotions, gestures, and multi-device synchronization.

## 🏗️ Architecture

### Backend Services (Python + FastAPI)
- **auth_service**: User authentication, JWT tokens, OAuth integration
- **ai_service**: LLM integration, conversation management, context handling  
- **streaming_service**: Real-time voice processing (STT/TTS), WebSocket handling
- **shared**: Common models, utilities, CLI interfaces

### Frontend Applications
- **web_app** (Next.js): Dashboard, settings, marketplace, user management
- **mobile_app** (React Native): Mobile interface for conversation and customization
- **unity_client** (Unity 2022+): 3D rendering, hologram display, device integration

### Data Layer
- **PostgreSQL**: Primary database for user data, conversations, subscriptions
- **Redis**: Caching, session storage, pub/sub for real-time features
- **S3**: Asset storage for 3D models, voice samples, user content

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Unity 2022.3+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 6+

### Development Setup

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd holo-mate-platform
   ```

2. **Backend services**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend applications**
   ```bash
   cd frontend/web_app
   npm install
   npm run dev
   
   cd frontend/mobile_app
   npm install
   npm run start
   ```

4. **Unity client**
   - Open `unity_client/` in Unity 2022.3+
   - Install required packages (URP, AR Foundation)
   - Configure project settings

5. **Infrastructure**
   ```bash
   cd infrastructure
   terraform init
   terraform plan
   ```

## 📋 Development Tasks

This project follows Spec-Driven Development with 136 detailed tasks:

- **Phase 3.1**: Setup (T001-T013)
- **Phase 3.2**: Tests First - TDD (T014-T046) 
- **Phase 3.3**: Core Implementation (T047-T106)
- **Phase 3.4**: Integration (T107-T119)
- **Phase 3.5**: Polish (T120-T131)
- **Phase 3.6**: Release & Versioning (T132-T136)

See `docs/tasks.md` for complete task list.

## 🧪 Testing

### Test Structure
- **Contract Tests**: API endpoint validation
- **Integration Tests**: User story validation  
- **Unit Tests**: Component testing
- **E2E Tests**: Full user journey testing

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests  
cd frontend/web_app
npm test

# Unity tests
# Run in Unity Test Runner
```

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:
- Database connections
- AI service API keys
- Redis configuration
- S3 storage settings

### Database Setup
```bash
# Run migrations
cd backend
alembic upgrade head

# Seed test data
python scripts/seed_data.py
```

## 📚 Documentation

- **API Documentation**: `/docs/api.md`
- **Deployment Guide**: `/docs/deployment.md`
- **User Guide**: `/docs/user-guide.md`
- **Architecture**: `/docs/architecture.md`

## 🚀 Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
cd infrastructure
terraform apply
```

## 🤝 Contributing

1. Follow the task list in `docs/tasks.md`
2. Write tests before implementation (TDD)
3. Follow constitutional principles
4. Use conventional commits
5. Update documentation

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: https://docs.holo-mate.com
- **Community**: https://community.holo-mate.com  
- **Support**: support@holo-mate.com
- **Status**: https://status.holo-mate.com

---

**Built with Spec-Driven Development methodology**
