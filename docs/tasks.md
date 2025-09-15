# Tasks: Holo-Mate AI Companion Platform

**Input**: Design documents from `/specs/001-x-y-d/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Implementation plan loaded successfully
   → Extracted: Python + FastAPI, Unity 2022+, Next.js, PostgreSQL + Redis
2. Load optional design documents: ✓
   → data-model.md: 10 entities extracted → model tasks
   → contracts/: 50+ endpoints → contract test tasks
   → research.md: 12 technical decisions → setup tasks
3. Generate tasks by category: ✓
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules: ✓
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...) ✓
6. Generate dependency graph ✓
7. Create parallel execution examples ✓
8. Validate task completeness: ✓
   → All contracts have tests
   → All entities have models
   → All endpoints implemented
9. Return: SUCCESS (tasks ready for execution) ✓
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup
- [x] T001 Create project structure per implementation plan
- [x] T002 Initialize Python FastAPI backend services
- [ ] T003 Initialize Next.js web application
- [ ] T004 Initialize React Native mobile application
- [ ] T005 Initialize Unity 2022+ client project
- [ ] T006 [P] Configure Python linting (black, isort, flake8)
- [ ] T007 [P] Configure TypeScript/JavaScript linting (ESLint, Prettier)
- [ ] T008 [P] Configure Unity project settings and URP
- [ ] T009 [P] Setup Docker containers for all services
- [ ] T010 [P] Configure Terraform infrastructure templates
- [ ] T011 [P] Setup test database fixtures and migration system
- [ ] T012 [P] Configure semantic versioning (bump2version/changesets)
- [ ] T013 [P] Setup Unity asset pipeline (3D models, rigs, viseme mapping)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API Endpoints)
- [x] T014 [P] Contract test POST /auth/login in tests/contract/test_auth_login.py
- [x] T015 [P] Contract test POST /auth/refresh in tests/contract/test_auth_refresh.py
- [x] T016 [P] Contract test GET /users/me in tests/contract/test_users_me.py
- [x] T017 [P] Contract test PUT /users/me in tests/contract/test_users_update.py
- [x] T018 [P] Contract test GET /ai-companions in tests/contract/test_ai_companions_list.py
- [x] T019 [P] Contract test POST /ai-companions in tests/contract/test_ai_companions_create.py
- [x] T020 [P] Contract test GET /ai-companions/{id} in tests/contract/test_ai_companions_get.py
- [x] T021 [P] Contract test PUT /ai-companions/{id} in tests/contract/test_ai_companions_update.py
- [x] T022 [P] Contract test DELETE /ai-companions/{id} in tests/contract/test_ai_companions_delete.py
- [x] T023 [P] Contract test GET /conversations in tests/contract/test_conversations_list.py
- [x] T024 [P] Contract test POST /conversations in tests/contract/test_conversations_create.py
- [x] T025 [P] Contract test GET /conversations/{id} in tests/contract/test_conversations_get.py
- [x] T026 [P] Contract test PUT /conversations/{id} in tests/contract/test_conversations_update.py
- [x] T027 [P] Contract test GET /conversations/{id}/messages in tests/contract/test_messages_list.py
- [x] T028 [P] Contract test POST /streaming/chat in tests/contract/test_streaming_start.py
- [x] T029 [P] Contract test GET /streaming/chat/{id} in tests/contract/test_streaming_status.py
- [x] T030 [P] Contract test GET /devices in tests/contract/test_devices_list.py
- [x] T031 [P] Contract test POST /devices in tests/contract/test_devices_register.py
- [x] T032 [P] Contract test GET /devices/{id} in tests/contract/test_devices_get.py
- [x] T033 [P] Contract test PUT /devices/{id} in tests/contract/test_devices_update.py
- [x] T034 [P] Contract test GET /subscriptions in tests/contract/test_subscriptions_get.py
- [x] T035 [P] Contract test POST /subscriptions in tests/contract/test_subscriptions_create.py
- [x] T036 [P] Contract test GET /voice-profiles in tests/contract/test_voice_profiles_list.py

### Integration Tests (User Stories)
- [ ] T037 [P] Integration test user registration flow in tests/integration/test_user_registration.py
- [ ] T038 [P] Integration test AI companion creation in tests/integration/test_companion_creation.py
- [ ] T039 [P] Integration test voice conversation flow in tests/integration/test_voice_conversation.py
- [ ] T040 [P] Integration test device pairing in tests/integration/test_device_pairing.py
- [ ] T041 [P] Integration test subscription management in tests/integration/test_subscription_management.py
- [ ] T042 [P] Integration test multi-device sync in tests/integration/test_multi_device_sync.py
- [ ] T043 [P] Integration test GDPR compliance in tests/integration/test_gdpr_compliance.py
- [ ] T044 [P] Integration test full-duplex streaming in tests/integration/test_full_duplex_streaming.py
- [ ] T045 [P] Integration test multi-user conversation in tests/integration/test_multi_user_conversation.py
- [ ] T046 [P] Integration test user data erasure flow in tests/integration/test_data_erasure.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models (Entities)
- [ ] T047 [P] User model in backend/shared/src/models/user.py
- [ ] T048 [P] AICompanion model in backend/shared/src/models/ai_companion.py
- [ ] T049 [P] Conversation model in backend/shared/src/models/conversation.py
- [ ] T050 [P] Message model in backend/shared/src/models/message.py
- [ ] T051 [P] HologramDevice model in backend/shared/src/models/hologram_device.py
- [ ] T052 [P] CharacterAsset model in backend/shared/src/models/character_asset.py
- [ ] T053 [P] Subscription model in backend/shared/src/models/subscription.py
- [ ] T054 [P] UserPreference model in backend/shared/src/models/user_preference.py
- [ ] T055 [P] VoiceProfile model in backend/shared/src/models/voice_profile.py
- [ ] T056 [P] AnimationSequence model in backend/shared/src/models/animation_sequence.py

### Service Layer
- [ ] T057 [P] UserService CRUD in backend/auth_service/src/services/user_service.py
- [ ] T058 [P] AICompanionService in backend/ai_service/src/services/ai_companion_service.py
- [ ] T059 [P] ConversationService in backend/ai_service/src/services/conversation_service.py
- [ ] T060 [P] MessageService in backend/ai_service/src/services/message_service.py
- [ ] T061 [P] StreamingService in backend/streaming_service/src/services/streaming_service.py
- [ ] T062 [P] DeviceService in backend/streaming_service/src/services/device_service.py
- [ ] T063 [P] SubscriptionService in backend/auth_service/src/services/subscription_service.py
- [ ] T064 [P] VoiceProfileService in backend/ai_service/src/services/voice_profile_service.py

### CLI Commands
- [ ] T065 [P] CLI --create-user in backend/auth_service/src/cli/user_commands.py
- [ ] T066 [P] CLI --create-companion in backend/ai_service/src/cli/companion_commands.py
- [ ] T067 [P] CLI --start-conversation in backend/ai_service/src/cli/conversation_commands.py
- [ ] T068 [P] CLI --register-device in backend/streaming_service/src/cli/device_commands.py
- [ ] T069 [P] CLI --test-streaming in backend/streaming_service/src/cli/streaming_commands.py

### API Endpoints Implementation
- [ ] T070 POST /auth/login endpoint in backend/auth_service/src/api/auth.py
- [ ] T071 POST /auth/refresh endpoint in backend/auth_service/src/api/auth.py
- [ ] T072 GET /users/me endpoint in backend/auth_service/src/api/users.py
- [ ] T073 PUT /users/me endpoint in backend/auth_service/src/api/users.py
- [ ] T074 GET /ai-companions endpoint in backend/ai_service/src/api/ai_companions.py
- [ ] T075 POST /ai-companions endpoint in backend/ai_service/src/api/ai_companions.py
- [ ] T076 GET /ai-companions/{id} endpoint in backend/ai_service/src/api/ai_companions.py
- [ ] T077 PUT /ai-companions/{id} endpoint in backend/ai_service/src/api/ai_companions.py
- [ ] T078 DELETE /ai-companions/{id} endpoint in backend/ai_service/src/api/ai_companions.py
- [ ] T079 GET /conversations endpoint in backend/ai_service/src/api/conversations.py
- [ ] T080 POST /conversations endpoint in backend/ai_service/src/api/conversations.py
- [ ] T081 GET /conversations/{id} endpoint in backend/ai_service/src/api/conversations.py
- [ ] T082 PUT /conversations/{id} endpoint in backend/ai_service/src/api/conversations.py
- [ ] T083 GET /conversations/{id}/messages endpoint in backend/ai_service/src/api/messages.py
- [ ] T084 POST /streaming/chat endpoint in backend/streaming_service/src/api/streaming.py
- [ ] T085 GET /streaming/chat/{id} endpoint in backend/streaming_service/src/api/streaming.py
- [ ] T086 GET /devices endpoint in backend/streaming_service/src/api/devices.py
- [ ] T087 POST /devices endpoint in backend/streaming_service/src/api/devices.py
- [ ] T088 GET /devices/{id} endpoint in backend/streaming_service/src/api/devices.py
- [ ] T089 PUT /devices/{id} endpoint in backend/streaming_service/src/api/devices.py
- [ ] T090 GET /subscriptions endpoint in backend/auth_service/src/api/subscriptions.py
- [ ] T091 POST /subscriptions endpoint in backend/auth_service/src/api/subscriptions.py
- [ ] T092 GET /voice-profiles endpoint in backend/ai_service/src/api/voice_profiles.py

### Frontend Components
- [ ] T093 [P] User authentication components in frontend/web_app/src/components/auth/
- [ ] T094 [P] AI companion management components in frontend/web_app/src/components/companions/
- [ ] T095 [P] Conversation interface components in frontend/web_app/src/components/conversations/
- [ ] T096 [P] Device management components in frontend/web_app/src/components/devices/
- [ ] T097 [P] Subscription management components in frontend/web_app/src/components/subscriptions/
- [ ] T098 [P] Mobile conversation interface in frontend/mobile_app/src/screens/ConversationScreen.tsx
- [ ] T099 [P] Mobile companion management in frontend/mobile_app/src/screens/CompanionScreen.tsx
- [ ] T100 [P] Mobile device settings in frontend/mobile_app/src/screens/DeviceScreen.tsx

### Unity Client
- [ ] T101 [P] 3D character rendering system in unity_client/Assets/Scripts/Rendering/
- [ ] T102 [P] Voice streaming client in unity_client/Assets/Scripts/Streaming/
- [ ] T103 [P] Device communication in unity_client/Assets/Scripts/Device/
- [ ] T104 [P] Animation controller in unity_client/Assets/Scripts/Animation/
- [ ] T105 [P] Lip-sync system in unity_client/Assets/Scripts/LipSync/
- [ ] T106 [P] AI emotion mapping system in unity_client/Assets/Scripts/Emotion/

## Phase 3.4: Integration
- [ ] T107 Database connection and migration setup
- [ ] T108 Redis connection and caching setup
- [ ] T109 JWT authentication middleware
- [ ] T110 CORS and security headers
- [ ] T111 Request/response logging middleware
- [ ] T112 Error handling middleware
- [ ] T113 Rate limiting middleware
- [ ] T114 WebSocket connection handling
- [ ] T115 AI service integration (OpenAI, ElevenLabs)
- [ ] T116 Stripe payment integration
- [ ] T117 S3 asset storage integration
- [ ] T118 Monitoring and observability setup (Prometheus, Grafana, CloudWatch)
- [ ] T119 OpenTelemetry tracing setup for AI flow (STT→LLM→TTS)

## Phase 3.5: Polish
- [ ] T120 [P] Unit tests for validation in tests/unit/test_validation.py
- [ ] T121 [P] Unit tests for services in tests/unit/test_services.py
- [ ] T122 [P] Unit tests for models in tests/unit/test_models.py
- [ ] T123 Performance tests for API endpoints (<200ms)
- [ ] T124 Load tests for streaming connections (5k concurrent)
- [ ] T125 Security tests (authentication, authorization)
- [ ] T126 [P] Update API documentation in docs/api.md
- [ ] T127 [P] Update deployment documentation in docs/deployment.md
- [ ] T128 [P] Update user guide in docs/user-guide.md
- [ ] T129 Code review and refactoring
- [ ] T130 Remove code duplication
- [ ] T131 Run manual testing scenarios

## Phase 3.6: Release & Versioning
- [ ] T132 [P] Setup GitHub Actions release pipeline (Docker push + tag)
- [ ] T133 [P] Configure automated semantic versioning
- [ ] T134 [P] Setup production deployment pipeline
- [ ] T135 [P] Configure monitoring alerts and dashboards
- [ ] T136 [P] Setup backup and disaster recovery procedures

## Dependencies
- Tests (T014-T046) before implementation (T047-T106)
- Models (T047-T056) before services (T057-T064)
- Services before endpoints (T070-T092)
- Endpoints before frontend (T093-T100)
- Frontend before Unity client (T101-T106)
- Core implementation before integration (T107-T119)
- Integration before polish (T120-T131)
- Polish before release (T132-T136)

## Parallel Execution Examples

### Phase 3.1 Setup (T006-T013)
```
# Launch setup tasks in parallel:
Task: "Configure Python linting (black, isort, flake8)"
Task: "Configure TypeScript/JavaScript linting (ESLint, Prettier)"
Task: "Configure Unity project settings and URP"
Task: "Setup Docker containers for all services"
Task: "Configure Terraform infrastructure templates"
Task: "Setup test database fixtures and migration system"
Task: "Configure semantic versioning (bump2version/changesets)"
Task: "Setup Unity asset pipeline (3D models, rigs, viseme mapping)"
```

### Phase 3.2 Contract Tests (T014-T036)
```
# Launch contract tests in parallel:
Task: "Contract test POST /auth/login in tests/contract/test_auth_login.py"
Task: "Contract test GET /users/me in tests/contract/test_users_me.py"
Task: "Contract test POST /ai-companions in tests/contract/test_ai_companions_create.py"
Task: "Contract test GET /conversations in tests/contract/test_conversations_list.py"
Task: "Contract test POST /streaming/chat in tests/contract/test_streaming_start.py"
```

### Phase 3.3 Data Models (T047-T056)
```
# Launch model creation in parallel:
Task: "User model in backend/shared/src/models/user.py"
Task: "AICompanion model in backend/shared/src/models/ai_companion.py"
Task: "Conversation model in backend/shared/src/models/conversation.py"
Task: "Message model in backend/shared/src/models/message.py"
Task: "HologramDevice model in backend/shared/src/models/hologram_device.py"
```

### Phase 3.3 Service Layer (T057-T064)
```
# Launch service creation in parallel:
Task: "UserService CRUD in backend/auth_service/src/services/user_service.py"
Task: "AICompanionService in backend/ai_service/src/services/ai_companion_service.py"
Task: "ConversationService in backend/ai_service/src/services/conversation_service.py"
Task: "StreamingService in backend/streaming_service/src/services/streaming_service.py"
Task: "DeviceService in backend/streaming_service/src/services/device_service.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
- Follow TDD: Red → Green → Refactor cycle
- Use real dependencies in integration tests
- Maintain constitutional principles throughout

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**: 50+ endpoints → contract test tasks [P]
2. **From Data Model**: 10 entities → model creation tasks [P]
3. **From User Stories**: 9 scenarios → integration test tasks [P]
4. **Ordering**: Setup → Tests → Models → Services → Endpoints → Polish → Release
5. **Dependencies**: Tests block implementation, models block services

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Added missing tasks: test DB fixtures, full-duplex streaming, GDPR data erasure
- [x] Added Unity asset pipeline and AI emotion mapping
- [x] Added monitoring, tracing, and release pipeline tasks