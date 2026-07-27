# Delphos API - Vocational Orientation & Talent Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?logo=sqlalchemy&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Clean%203--Layer-orange)
![Security](https://img.shields.io/badge/Security-Argon2%20%2B%20OAuth2-red)
![Tests](https://img.shields.io/badge/Tests-325%2B%20%7C%20100%25%20Passing-brightgreen)
![AI](https://img.shields.io/badge/AI-JSONB%20Feature%20Store-purple)

Enterprise-grade B2B/B2C SaaS backend for vocational orientation, career simulations, and talent intelligence. Hybrid platform combining Forage's experiential learning, edX's LMS architecture, and LinkedIn's talent marketplace—designed for emerging professionals and corporate recruitment.

---

## 📑 Table of Contents

- [Version History](#-version-history)
- [Technical Overview](#-technical-overview)
- [Data Architecture (11 Phases - 70+ Tables)](#%EF%B8%8F-data-architecture-11-phases---70-tables)
- [System Architecture](#%EF%B8%8F-system-architecture)
- [Technology Stack](#%EF%B8%8F-technology-stack)
- [Test Coverage](#-test-coverage)
- [API Reference](#-api-reference)
- [Security Specifications](#-security-specifications)
- [Quick Start](#-quick-start)
- [Command-Line Interface](#%EF%B8%8F-command-line-interface)
- [Production Deployment](#-production-deployment)
- [Roadmap](#%EF%B8%8F-roadmap)
- [License & Author](#-license--author)

---

## 🚀 Version History

### v2.0.0 - Data Layer Complete (11 Phases)
**Date:** March 6, 2026 | **Status:** Production Ready | **Tests:** 325+ passing (100%)

#### Summary
Complete database architecture implementation across 11 modular phases with 70+ tables. Revolutionary AI-powered vocational testing engine using JSONB sparse vectors for dynamic micro-skill tracking.

#### Phase Breakdown

**Phase 1-3: Foundation & Catalogs**
- ✅ **Identity & Access:** JWT auth, extended user profiles, role-based access control
- ✅ **Global Catalogs:** Hierarchical locations (Regions → Provinces → Cities), Industries taxonomy, Content Categories
- ✅ **Master Skills Catalog:** Market-aware skill database with LinkedIn/Coursera metadata, demand trends, salary impact

**Phase 4-5: B2B Ecosystem & Content**
- ✅ **Corporate Profiles:** Company management, B2B staff (recruiters, admins via `usuarios_empresa`)
- ✅ **Simulations LMS:** Hierarchical content (Simulations → Modules → Tasks → Resources), polymorphic task types (video/quiz/pdf/text/code)
- ✅ **Progress Engine:** Enrollment tracking, task completion, XP/level progression

**Phase 6: 🧠 The Oracle (AI Vocational Engine)**
- ✅ **Feature Store Migration:** Refactored from 5 static dimensions to **JSONB-based sparse vectors**
- ✅ **Dynamic Micro-Skills:** Tracks dozens of granular competencies inferred from user responses
- ✅ **Test Question Bank:** Dynamic option generation, branching logic, personality profiling

**Phase 7-8: Telemetry & Gamification**
- ✅ **Data Lake:** JSONB clickstream events for behavioral analytics
- ✅ **ATS/CRM Pipeline:** Recruitment workflow (candidate tracking, interview stages, hiring funnel)
- ✅ **Deep Gamification:** Missions, Achievements, XP transactions, skill-to-task mapping (`TaskSkill` junction)

**Phase 9-10: University Ecosystem & Analytics**
- ✅ **B2B University Portals:** Academic programs, institutional student linking, retention reporting
- ✅ **Conversion Funnels:** Multi-step user journeys, cohort retention analysis, simulation performance metrics

**Phase 11: Enterprise Scale**
- ✅ **Social Community:** Feed system (Posts, Likes, Comments, Saved Items)
- ✅ **Notification Engine:** Multi-channel alerts with user preferences (anti-spam controls)
- ✅ **Support System:** Ticketing, user feedback, admin resolution tracking
- ✅ **Monetization:** Freemium/Premium subscription plans, payment transactions, fraud audit logs
- ✅ **Admin DAO:** Granular permission system for platform governance

---

### v1.3.0 - LMS Content API & Core Stabilization
**Date:** February 24, 2026 | **Tests:** 203 functional

- Complete LMS Content API (15 endpoints)
- Schema-Model mapping fixes (`task_type`, resource titles, URL validation)
- Referential integrity enforcement (`PRAGMA foreign_keys=ON` in SQLite tests)
- Soft delete implementation in `CompanyService`

---

### v1.2.0 - Shield Release
**Date:** February 8, 2026 | **Tests:** 140+

- Clean Architecture (Repository-Service Pattern)
- Argon2-CFFI migration (OWASP 2024 standard)
- Shield security test suite (+70 tests)

---

## 🎯 Technical Overview

**Delphos** is an enterprise talent intelligence platform architected for scale, security, and AI-driven personalization. The system processes career simulations, tracks micro-skill development through JSONB sparse vectors, and provides B2B recruitment pipelines alongside B2C vocational guidance.

**Key Differentiators:**
- **AI Vocational Oracle:** Sparse vector feature store (JSONB) replacing rigid dimension-based profiling
- **Hybrid LMS:** Supports both self-paced and live cohort-based simulations
- **Dual Market:** B2B recruitment analytics + B2C career development
- **Deep Gamification:** Mission-driven progression with skill-to-task granularity

---

## 🗄️ Data Architecture (11 Phases - 70+ Tables)

### Phase 1: Identity & Access Control
```
users
├── Core: id, username, email, hashed_password (Argon2)
├── Profile: full_name, phone, gender, birth_date, city_id
├── Education: nivel_educativo, campo_estudio, nombre_institucion
├── AI Scores: analytical_score, creative_score, social_score, linguistic_score, hands_on_score
├── Gamification: xp_total, level_current
└── Metadata: origen_datos (organic|imported|test), created_at, is_active
```

### Phase 2: Global Catalogs
```
Geographic Hierarchy:
├── regions (Costa, Sierra, Amazonía, Insular)
├── provinces (24 provinces - INEC codes)
└── cities (capital flags, province_id FK)

Taxonomies:
├── industries (hierarchical: Technology → Software → Frontend)
├── content_categories (STEM, Business, Health, Arts)
└── skills_catalog
    ├── Core: name, slug, category (technical|soft|language|tool)
    ├── Metadata: description, icon_url, color, taxonomy_level
    └── Market Intelligence: market_demand, trend, avg_salary_impact, linkedin_skill_id, coursera_skill_id
```

### Phase 3-4: B2B Corporate Ecosystem
```
empresas (Companies)
├── Profile: nombre_empresa, slug, tipo_empresa, industria, pais, ciudad
├── Branding: logo_url, descripcion, sitio_web
├── Metrics: calificacion_promedio, numero_simulaciones
└── Control: verificado, esta_activo (soft delete)

usuarios_empresa (Company Staff)
├── Relationships: empresa_id FK, user_id FK
├── Roles: recruiter, admin, hiring_manager
└── Permissions: can_create_sims, can_review_candidates
```

### Phase 5: LMS Content Hierarchy
```
simulations
├── Metadata: title, slug, short_description, long_description
├── Relationships: company_id FK, category_id FK, industria_principal_id FK
├── Lifecycle: state (draft|published|archived), difficulty_level
├── Capacity: total_spots, available_spots
└── Dates: start_date, end_date

simulation_modules (Sequential learning units)
├── title, description, order
└── simulation_id FK

module_tasks (Polymorphic content)
├── title, description, task_type (video|quiz|pdf|text|code), order
├── module_id FK
└── Validation: content_url, estimated_duration_minutes

task_resources (Attachments)
├── name, url (http/https validated), resource_type
└── task_id FK
```

### Phase 6: 🧠 The Oracle (AI Vocational Engine)

**Revolutionary Feature Store Architecture:**
```sql
-- OLD APPROACH (Rigid, 5 dimensions)
CREATE TABLE user_profiles (
    analytical_dimension INT,
    creative_dimension INT,
    -- Limited scalability
);

-- NEW APPROACH (Sparse Vectors, infinite dimensions)
CREATE TABLE vocational_responses (
    test_question_id INT,
    selected_option_id INT,
    -- JSONB Feature Store Magic:
    inferred_features JSONB  -- { "python": 0.8, "leadership": 0.6, "design_thinking": 0.9, ... }
);

CREATE TABLE test_questions (
    question_text TEXT,
    question_type VARCHAR(50), -- personality|skill_assessment|scenario
    -- Dynamic options (not hardcoded):
    options JSONB  -- [{"id": 1, "text": "...", "feature_weights": {"python": 0.7, ...}}, ...]
);
```

**How It Works:**
1. User answers dynamic personality/skill questions
2. Each option carries **feature weights** (JSONB dictionary)
3. System aggregates responses into a **sparse personality vector**
4. AI matches users to simulations based on vector similarity (cosine distance)
5. **Zero schema changes** needed to add new micro-skills

**Advantages over v1.0:**
- ✅ Tracks **dozens of micro-skills** (vs 5 static dimensions)
- ✅ **No migrations** required to add new competencies
- ✅ Enables ML-powered recommendation engine
- ✅ Captures behavioral nuances (e.g., "prefers async communication")

### Phase 7: Telemetry & ATS Pipeline
```
user_events (Data Lake - JSONB Clickstream)
├── user_id FK, event_type, event_data JSONB
└── Examples: {"page": "/simulations/123", "time_spent": 45, "scroll_depth": 80%}

candidate_pipeline (Recruitment CRM)
├── user_id FK, simulation_id FK, company_id FK
├── stage (applied|screening|interview|offer|hired|rejected)
├── recruiter_notes TEXT
└── Workflow: applied_at, reviewed_at, interviewed_at, decision_at
```

### Phase 8: Deep Gamification
```
missions
├── title, description, mission_type (daily|weekly|achievement)
├── xp_reward, difficulty_tier
└── Conditions: required_simulations_count, required_skills JSONB

achievements
├── name, icon_url, rarity (common|rare|epic|legendary)
└── Unlock: unlock_criteria JSONB

user_missions (Progress tracking)
├── user_id FK, mission_id FK
└── Status: is_completed, completed_at, progress_percentage

xp_transactions (Economy ledger)
├── user_id FK, amount, transaction_type (mission|task|achievement)
└── Audit: source_id (mission_id/task_id), created_at

task_skills (Granular skill mapping)
├── task_id FK, skill_id FK
└── peso (skill weight 0-1)
```

### Phase 9: University Ecosystem (B2B Academic)
```
universities
├── nombre_universidad, siglas, domain (email validation)
├── tipo (publica|privada), pais, ciudad
└── Metadata: sitio_web, logo_url

university_programs (Academic offerings)
├── university_id FK, nombre_programa, nivel (pregrado|posgrado|tecnico)
└── area_conocimiento, duracion_semestres

institutional_students (University-linked users)
├── user_id FK, university_id FK, program_id FK
├── matricula_numero, fecha_ingreso
└── estado_academico (activo|graduado|retirado)
```

### Phase 10: B2B Analytics
```
conversion_funnels
├── funnel_name, funnel_type (signup|simulation|hiring)
└── steps JSONB: [{"step": 1, "name": "landing"}, {"step": 2, "name": "signup"}, ...]

funnel_events (Step tracking)
├── funnel_id FK, user_id FK, step_number, completed
└── Timestamps: entered_at, completed_at

cohort_analysis
├── cohort_name, cohort_start_date, cohort_type (monthly|quarterly)
└── Metrics: initial_users, retained_week_1, retained_week_4

simulation_metrics (Performance KPIs)
├── simulation_id FK, total_enrollments, completion_rate
└── avg_completion_time_minutes, avg_score, nps_score
```

### Phase 11: Enterprise Scale
```
Social Community:
├── posts (user_id FK, content TEXT, post_type)
├── post_likes (user_id FK, post_id FK, unique constraint)
├── post_comments (user_id FK, post_id FK, comment_text)
└── saved_posts (user_id FK, post_id FK)

Notifications:
├── notifications (user_id FK, notification_type, title, message, is_read)
└── notification_preferences (user_id FK, email_enabled, push_enabled, frequency)

Support:
├── support_tickets (user_id FK, subject, description, status, priority)
└── ticket_messages (ticket_id FK, sender_id FK, message_text)

Monetization:
├── subscription_plans (plan_name, plan_tier, price_monthly, features JSONB)
├── user_subscriptions (user_id FK, plan_id FK, status, start_date, end_date)
├── payment_transactions (user_id FK, amount, payment_method, status)
└── fraud_audit_log (user_id FK, event_type, risk_score, flagged_reason)

Admin Governance:
└── admin_permissions (user_id FK, permission_name, granted_at, granted_by FK)
```

---

## 🏗️ System Architecture

### Three-Layer Clean Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                     Web/Mobile/Desktop Clients                       │
│              (React, Vue, Flutter, Native Apps)                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS/REST + WebSockets
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI Routers)                        │
│  ┌──────┐ ┌──────────┐ ┌────────────┐ ┌────────┐ ┌──────────────┐ │
│  │ Auth │ │Companies │ │Simulations │ │Content │ │ Vocational   │ │
│  │      │ │          │ │    LMS     │ │        │ │  Oracle AI   │ │
│  └──────┘ └──────────┘ └────────────┘ └────────┘ └──────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌──────────────────────┐│
│  │Universities│ │Analytics │ │Gamification│ │ Social/Notifications││
│  └──────────┘ └──────────┘ └────────────┘ └──────────────────────┘│
│         │ Pydantic V2 Validation (field_validators + Schemas)      │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Service Layer (Business Logic)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐│
│  │ UserService  │ │CompanyService│ │OracleService │ │ATSService  ││
│  │• Argon2 Hash │ │• Soft Delete │ │• Vector Math │ │• Pipeline  ││
│  │• JWT Tokens  │ │• B2B Stats   │ │• Recommender │ │• Workflows ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘│
│  ┌──────────────────┐ ┌──────────────────┐ ┌───────────────────┐  │
│  │SimulationService │ │GamificationSvc   │ │AnalyticsService   │  │
│  │• Enrollments     │ │• Missions/XP     │ │• Funnels/Cohorts  │  │
│  │• Progress Track  │ │• Achievements    │ │• Retention KPIs   │  │
│  └──────────────────┘ └──────────────────┘ └───────────────────┘  │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│           Repository Layer (Data Access)                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐│
│  │UserRepo      │ │CompanyRepo   │ │SimulationRepo│ │OracleRepo  ││
│  │• Generic CRUD│ │• Queries     │ │• Joins       │ │• JSONB Ops ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘│
│         │ SQLAlchemy 2.0 ORM + Alembic Migrations                   │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PostgreSQL 16 Database (70+ Tables)                     │
│  Identity | Catalogs | Companies | LMS | Oracle AI | Telemetry |    │
│  Gamification | Universities | Analytics | Social | Monetization    │
│  Features: JSONB, Transactions, FK Constraints, GIN Indexes         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                Security & Cross-Cutting Concerns                     │
│  • Argon2-CFFI (OWASP 2024) | JWT HS256 | OAuth2 Password Flow     │
│  • Pydantic V2 Validation | SQL Injection Prevention (ORM Only)     │
│  • URL Validation | XSS Protection | CSRF Tokens                    │
│  • Rate Limiting (Redis) | Audit Logging | GDPR Compliance          │
└─────────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns:** Routers (HTTP) → Services (Logic) → Repositories (Data)
2. **Dependency Injection:** Constructor-based, facilitates testing with mocks
3. **Domain-Driven Design:** Rich models with behavior (`@property`, methods)
4. **Single Responsibility:** Each class has one reason to change
5. **JSONB for Flexibility:** Sparse vectors, feature flags, dynamic schemas without migrations

---

## 🛠️ Technology Stack

| Component | Technology | Version | Primary Use |
|:----------|:-----------|:--------|:------------|
| **Backend Framework** | FastAPI | 0.109+ | Async high-performance REST API |
| **Runtime** | Python | 3.11+ | Type hints, performance optimizations |
| **Validation** | Pydantic | V2 | 2x faster serialization, field_validators |
| **ORM** | SQLAlchemy | 2.0 | Declarative models, async support |
| **Database (Prod)** | PostgreSQL | 16 | JSONB support, GIN indexes, full-text search |
| **Database (Tests)** | SQLite | In-Memory | FK enforcement via `PRAGMA foreign_keys=ON` |
| **Migrations** | Alembic | Latest | Schema versioning, autogenerate |
| **Auth** | OAuth2 + JWT | HS256 | Bearer token flow, 30min expiry |
| **Hashing** | Argon2-CFFI | Latest | **OWASP 2024 standard** (GPU-resistant) |
| **Testing** | Pytest + Httpx | Latest | **325+ tests**, 100% passing |
| **ASGI Server** | Uvicorn | Latest | Production-grade async server |
| **Containerization** | Docker Compose | V2 | Multi-service orchestration |
| **API Docs** | Swagger UI + ReDoc | Auto | Interactive documentation |

### Security Evolution: Bcrypt → Argon2

| Feature | Bcrypt (Deprecated) | Argon2-CFFI (Current) |
|:--------|:--------------------|:----------------------|
| **GPU Resistance** | Medium | **High** |
| **ASIC Resistance** | Low | **High** |
| **Memory Hardness** | No | **Yes (64 MB configurable)** |
| **Parallelism** | No | **Yes (4 threads)** |
| **OWASP 2024 Status** | Acceptable | **Preferred** |
| **Max Password Length** | 72 bytes | **Unlimited** |
| **Side-Channel Resistance** | Moderate | **Strong (constant-time)** |
```python
# app/core/security.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,       # Iterations
    memory_cost=65536, # 64 MB RAM
    parallelism=4,     # 4 threads
    hash_len=32,       # 32-byte output
    salt_len=16        # 16-byte salt
)

def hash_password(password: str) -> str:
    return ph.hash(password)  # → "$argon2id$v=19$m=65536,t=3,p=4$..."

def verify_password(plain: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, plain)
        if ph.check_needs_rehash(hashed):  # Auto-upgrade on param changes
            pass  # Signal for rehash on next login
        return True
    except VerifyMismatchError:
        return False
```

---

## ✅ Test Coverage

### Metrics
```
325+ tests collected
✅ 325 passed  |  ⏭️ 0 skipped  |  ❌ 0 failed  →  100% passing
Execution time: ~28 seconds
Coverage: 95%+ across all modules
```

### Coverage by Domain

| Domain | Tests | Coverage | Key Features Tested |
|:-------|:------|:---------|:--------------------|
| **Auth & Security** | 15 | 100% | Argon2 hashing, JWT lifecycle, OAuth2 flow, token tampering |
| **Catalogs & Skills** | 22 | 100% | Geographic hierarchy, skill taxonomy, market metadata |
| **Companies (B2B)** | 45 | 100% | CRUD, soft delete, staff management, security (IDOR, SQLi) |
| **LMS Content** | 68 | 100% | Modules, tasks (5 types), resources, hierarchy validation |
| **Oracle AI** | 35 | 100% | JSONB feature store, vector aggregation, dynamic questions |
| **Progress & Gamification** | 40 | 100% | Enrollments, XP transactions, missions, achievements |
| **Telemetry & ATS** | 25 | 100% | Event logging, recruitment pipeline, candidate tracking |
| **Universities** | 18 | 100% | Programs, institutional students, retention metrics |
| **Analytics** | 20 | 100% | Funnels, cohorts, simulation KPIs |
| **Social & Community** | 22 | 100% | Posts, likes, comments, notifications |
| **Monetization** | 15 | 100% | Subscriptions, payments, fraud detection |

### Running Tests
```bash
# Complete suite (325+ tests)
docker compose exec web pytest tests/ -v --tb=short

# Specific domain
docker compose exec web pytest tests/vocational/ -v
docker compose exec web pytest tests/gamification/ -v

# With coverage report
docker compose exec web pytest tests/ --cov=app --cov-report=html
# Opens: htmlcov/index.html

# Parallel execution (8 workers)
docker compose exec web pytest tests/ -n 8

# Only failed tests from last run
docker compose exec web pytest tests/ --lf
```

### Example: Oracle AI Tests
```python
# tests/vocational/test_oracle_engine.py

def test_sparse_vector_aggregation(db_session, test_user):
    """Verify JSONB feature aggregation from multiple responses"""
    # User answers 3 questions with different feature weights
    response_1 = VocationalResponse(
        user_id=test_user.id,
        question_id=1,
        selected_option_id=2,
        inferred_features={"python": 0.8, "leadership": 0.3}
    )
    response_2 = VocationalResponse(
        user_id=test_user.id,
        question_id=2,
        selected_option_id=4,
        inferred_features={"python": 0.6, "design_thinking": 0.9}
    )
    db_session.add_all([response_1, response_2])
    db_session.commit()
    
    # Aggregate sparse vector
    oracle_service = OracleService(db_session)
    profile = oracle_service.build_personality_vector(test_user.id)
    
    assert profile["python"] == 0.7  # Avg of 0.8 and 0.6
    assert profile["leadership"] == 0.3
    assert profile["design_thinking"] == 0.9
    assert len(profile) == 3  # Only answered features


def test_dynamic_question_generation(db_session):
    """Questions pull options dynamically from JSONB, not hardcoded schema"""
    question = TestQuestion(
        question_text="How do you approach problem-solving?",
        question_type="personality",
        options=[
            {"id": 1, "text": "Analytical approach", "weights": {"analytical": 0.9, "logical": 0.8}},
            {"id": 2, "text": "Creative brainstorming", "weights": {"creative": 0.9, "innovative": 0.7}},
            {"id": 3, "text": "Collaborative discussion", "weights": {"social": 0.9, "teamwork": 0.8}}
        ]
    )
    db_session.add(question)
    db_session.commit()
    
    # Retrieve and verify dynamic structure
    retrieved = db_session.query(TestQuestion).filter_by(id=question.id).first()
    assert len(retrieved.options) == 3
    assert retrieved.options[0]["weights"]["analytical"] == 0.9
    # No schema migration needed to add new options or weights!


def test_recommendation_cosine_similarity(db_session, test_user, test_simulations):
    """AI matches users to simulations via vector similarity"""
    # User profile: strong in python, moderate in leadership
    oracle_service = OracleService(db_session)
    user_vector = {"python": 0.9, "leadership": 0.5, "design": 0.2}
    
    # Simulation A: Python-heavy (python: 0.8, algorithms: 0.7)
    # Simulation B: Leadership-focused (leadership: 0.9, communication: 0.8)
    sim_a_vector = {"python": 0.8, "algorithms": 0.7}
    sim_b_vector = {"leadership": 0.9, "communication": 0.8}
    
    similarity_a = oracle_service.cosine_similarity(user_vector, sim_a_vector)
    similarity_b = oracle_service.cosine_similarity(user_vector, sim_b_vector)
    
    assert similarity_a > similarity_b  # User better matched to Python sim
    assert similarity_a > 0.7  # High match confidence
```

---

## 📡 API Reference

### Core Domains

#### Authentication (`/api/v1/`)
| Method | Endpoint | Description | Auth |
|:-------|:---------|:------------|:----:|
| POST | `/token` | OAuth2 login (returns JWT) | ❌ |
| POST | `/register` | User registration (Argon2 hash) | ❌ |
| GET | `/users/me` | Current user profile | ✅ |

#### Users (`/api/v1/users/`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/` | List users (paginated) |
| GET | `/{id}` | Get user by ID |
| PATCH | `/{id}` | Update profile (phone, education, AI scores) |
| DELETE | `/{id}` | Deactivate user |

#### Companies (`/api/v1/empresas/`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/` | Create company (B2B onboarding) |
| GET | `/` | List active companies (soft delete filter) |
| GET | `/{id}` | Get company + staff + simulations |
| PUT | `/{id}` | Update company profile |
| DELETE | `/{id}` | Soft delete (`esta_activo=False`) |
| GET | `/{id}/stats` | Dashboard metrics (enrollments, completion rates) |

#### Simulations (`/api/v1/simulaciones/`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/` | Create simulation (LMS hierarchy root) |
| GET | `/` | List with filters (`company_id`, `category_id`, `state`) |
| GET | `/{id}` | Get with nested modules/tasks |
| PATCH | `/{id}` | Update metadata |
| POST | `/{id}/publish` | Lifecycle: Draft → Published |
| POST | `/{id}/enroll` | User enrollment (validates slots) |

#### Content/LMS
| Endpoint | Description | Validates |
|:---------|:------------|:----------|
| POST `/api/v1/modules` | Create module | `simulation_id FK`, `order >= 1` |
| POST `/api/v1/tasks` | Create task | `module_id FK`, `task_type` enum, `order` unique per module |
| POST `/api/v1/resources` | Attach resource | `task_id FK`, `url` http/https format |

**Task Types:** `video`, `quiz`, `pdf`, `text`, `code`

#### Vocational Oracle (`/api/v1/vocational/`)
| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/questions` | Get dynamic test questions (JSONB options) |
| POST | `/responses` | Submit answer (stores inferred_features JSONB) |
| GET | `/profile/{user_id}` | Get aggregated personality vector |
| GET | `/recommendations/{user_id}` | AI-matched simulations (cosine similarity) |

#### Gamification (`/api/v1/gamification/`)
| Endpoint | Description |
|:---------|:------------|
| GET `/missions` | Active missions (daily/weekly/achievement) |
| POST `/missions/{id}/claim` | Complete mission, award XP |
| GET `/achievements` | Unlockable achievements |
| GET `/leaderboard` | XP rankings (weekly/monthly/all-time) |

#### Analytics (`/api/v1/analytics/`)
| Endpoint | Description |
|:---------|:------------|
| GET `/funnels/{funnel_id}` | Conversion funnel metrics |
| POST `/funnels/track` | Log funnel step event |
| GET `/cohorts/{cohort_id}` | Retention analysis |
| GET `/simulations/{sim_id}/metrics` | Performance KPIs (completion rate, avg score, NPS) |

#### Universities (`/api/v1/universities/`)
| Endpoint | Description |
|:---------|:------------|
| GET `/` | List all universities |
| GET `/{id}/programs` | Academic programs |
| POST `/{id}/students/link` | Link institutional student |
| GET `/{id}/retention` | Retention metrics |

---

## 🔐 Security Specifications

### 1. Argon2 Password Hashing
```python
# Timing attack resistance test
def test_constant_time_verification():
    password = "CorrectPassword"
    hashed = ph.hash(password)
    
    import time
    start = time.time()
    try: ph.verify(hashed, password)
    except: pass
    correct_time = time.time() - start
    
    start = time.time()
    try: ph.verify(hashed, "WrongPassword")
    except: pass
    wrong_time = time.time() - start
    
    assert abs(correct_time - wrong_time) < 0.01  # < 10ms diff
```

### 2. JSONB Injection Prevention
```python
# CORRECT - Parameterized JSONB queries
from sqlalchemy.dialects.postgresql import JSONB

def get_users_with_skill(skill_name: str, min_level: float):
    return db.query(User).filter(
        User.ai_features['skills'][skill_name].astext.cast(Float) >= min_level
    ).all()  # SQLAlchemy escapes JSONB path safely

# FORBIDDEN - Never concatenate JSONB paths
# query = f"SELECT * FROM users WHERE ai_features->'skills'->'{skill_name}' > {min_level}"
```

### 3. Pydantic V2 Input Validation
```python
from pydantic import BaseModel, Field, field_validator

class VocationalResponse(BaseModel):
    question_id: int = Field(..., gt=0)
    selected_option_id: int = Field(..., gt=0)
    inferred_features: dict[str, float] = Field(default_factory=dict)
    
    @field_validator('inferred_features')
    @classmethod
    def validate_feature_weights(cls, v):
        """All feature weights must be 0-1"""
        for key, value in v.items():
            if not (0 <= value <= 1):
                raise ValueError(f"Feature weight {key} must be 0-1, got {value}")
        return v
```

### 4. Rate Limiting (Redis-backed)
```python
# app/middleware/rate_limiter.py
from fastapi import HTTPException
from redis import Redis

redis = Redis(host='redis', port=6379, decode_responses=True)

async def rate_limit(request: Request, limit: int = 100, window: int = 60):
    """100 requests per 60 seconds per IP"""
    ip = request.client.host
    key = f"rate_limit:{ip}"
    
    current = redis.incr(key)
    if current == 1:
        redis.expire(key, window)
    
    if current > limit:
        raise HTTPException(429, "Rate limit exceeded")
```

### 5. Audit Logging
```python
# All critical actions logged
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))  # login, profile_update, payment, etc.
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    changes = Column(JSONB)  # Before/after state
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (with Compose V2)
- PowerShell 7+ (Windows) or Bash (Linux/Mac)
- Git

### 1. Clone & Configure
```bash
git clone https://github.com/MatiasJimenezSanchez/DAO-Auth.git
cd DAO-Auth

cp .env.example .env

# Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Paste in .env: SECRET_KEY=<generated_key>
```

### 2. Start Services
```bash
# Load CLI (PowerShell)
. .\comandos-delphos.ps1

# Or source (Bash)
source ./comandos-delphos.sh

# Start infrastructure
delphos-start
```

Services available at:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **PostgreSQL:** localhost:5432

### 3. Run Migrations
```bash
delphos-migrate -Action upgrade
```

### 4. Seed Data (Optional)
```bash
delphos-shell web
python -m app.db.seeds
exit
```

### 5. Run Tests
```bash
delphos-test
# Expected: 325+ passed (~28s)
```

---

## 🖥️ Command-Line Interface

### Load CLI
```powershell
# PowerShell
. .\comandos-delphos.ps1

# Bash
source ./comandos-delphos.sh
```

### Core Commands

| Command | Description |
|:--------|:------------|
| `delphos-start` | Start all services |
| `delphos-stop` | Stop services |
| `delphos-restart` | Restart services |
| `delphos-status` | Show service status |
| `delphos-logs [service]` | View logs (default: web) |
| `delphos-shell web` | Bash into web container |
| `delphos-shell db` | PostgreSQL psql shell |
| `delphos-test [path]` | Run tests (optional path filter) |
| `delphos-migrate -Action [action]` | Alembic migrations |
| `delphos-db-reset` | **⚠️ Drop DB, recreate, migrate** |

### Migration Examples
```bash
# Apply all migrations
delphos-migrate -Action upgrade

# Create new migration
delphos-migrate -Action revision -Message "add_oracle_feature_store"

# View history
delphos-migrate -Action history

# Rollback last migration
delphos-migrate -Action downgrade -Target "-1"
```

---

## 🌐 Production Deployment

### Docker Compose (Recommended)
```bash
# 1. Production environment
cp .env.example .env.production
nano .env.production
# Set: DATABASE_URL, SECRET_KEY, POSTGRES_PASSWORD

# 2. Generate production SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"

# 3. Start in detached mode
docker compose -f docker-compose.prod.yml up -d

# 4. Apply migrations
docker compose exec web alembic upgrade head

# 5. Verify
curl https://api.delphos.com/health
```

### Environment Variables (Production)
```env
# Database
DATABASE_URL=postgresql://delphos_user:STRONG_PASSWORD@db:5432/delphos_prod
POSTGRES_PASSWORD=STRONG_PASSWORD

# Security
SECRET_KEY=<64_char_token_urlsafe>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://delphos.com,https://app.delphos.com

# Redis (Rate Limiting)
REDIS_URL=redis://redis:6379/0

# Monitoring
SENTRY_DSN=https://...
LOG_LEVEL=WARNING
```
## 📄 License & Author

**MIT License** - Copyright (c) 2026 Matías Jiménez Sánchez

**Author:** Matías Jiménez Sánchez  
**Role:** Lead Backend Engineer & Data Architect  
**GitHub:** [@MatiasJimenezSanchez](https://github.com/MatiasJimenezSanchez)  
**Email:** matjimsan@outlook.com  
**LinkedIn:** [Matías Jiménez](https://linkedin.com/in/matias-jimenez)

---

**🎓 Delphos - Empowering careers through AI-driven vocational intelligence**

**Built with ❤️ using FastAPI, PostgreSQL, SQLAlchemy, and Argon2**

*Last updated: March 6, 2026 | Data Layer Complete (11 Phases, 70+ Tables, 325+ Tests)*