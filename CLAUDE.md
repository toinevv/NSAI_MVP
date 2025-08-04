# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Mission Statement

**To save 1,000,000 operator hours monthly by transforming how logistics companies capture, understand, and automate their operational workflows.**

## Project Overview

NewSystem.AI is an AI-powered screen recording and workflow analysis platform that helps logistics companies identify automation opportunities. The system records warehouse operator workflows and uses GPT-4V to analyze them for time savings and automation potential.

**The Core Problem**: The people who best understand what needs to be automated (operators) can't effectively communicate it to the people who build automation (engineers). This communication gap causes automation projects to fail even after $50K+ investments.

**Our Solution**: We become the essential translation layer between operational expertise and technical implementation, using screen recording + AI analysis to bridge this gap.

## Business Strategy & Go-to-Market Model

### Dual-Path Strategy
- **Platform Direct**: $2,500-5,000/month for immediate access - no pilot required for technical teams
- **Pilot Program**: $15K/4 weeks with 100% credit to annual contract - for teams wanting proof first
- **Both paths lead to same outcome**: Operational workflows transformed into working automation

### Market Entry Strategy
- **Wedge**: Start with email → WMS data entry (operators do this 15x daily, 2 min each)
- **Target**: Mid-size logistics companies (200-300 employees) drowning in manual data entry
- **Geographic Expansion**: Benelux (warm network) → US (ops leaders) → Global (platform enables)

### Customer Journey
**Direct Platform Path**: Day 1 signup → Week 1 first automation → Month 1 full team → Month 2+ implementation services
**Pilot-First Path**: Week 1-4 pilot proves 20+ hours/week saved → Month 2 platform access → Month 3+ scale proven model

## Competitive Positioning & Why We Win

### vs Process Mining (Celonis)
- **They**: Show what happened in systems
- **We**: Show what to do about human workflows
- **Advantage**: We focus on human workflows, they require IT integration

### vs RPA (UiPath) 
- **They**: Automate predefined processes
- **We**: Discover what to automate first
- **Advantage**: We adapt when processes change, they break

### vs Consultants (Accenture)
- **They**: Take months and millions, leave documents
- **We**: Deliver in weeks, create working automation
- **Advantage**: Our platform keeps learning after consultants leave

### Our Unique Advantage: Choice
Unlike pure software (UiPath) or pure consulting (Accenture), we offer flexible engagement models that fit any risk tolerance while delivering real automation.

## Cultural Principles (Guide All Development)

These principles should influence every development decision:

1. **Operators are heroes** - Make their expertise visible and valuable
   - *Code Impact*: UI copy speaks to logistics coordinators, not IT departments
   - *Feature Priority*: Operator-facing features get highest priority

2. **Automation enhances, not replaces** - Eliminate boring work, not jobs
   - *Code Impact*: Focus on "time saved for strategic work" messaging
   - *Feature Priority*: Build tools that augment human decision-making

3. **Reality over theory** - Build for how work actually happens
   - *Code Impact*: Test with real warehouse workflows, not synthetic data
   - *Feature Priority*: Observed patterns trump theoretical optimization

4. **Speed over perfection** - Fast iterations beat lengthy planning
   - *Code Impact*: Ship 80% solutions quickly, iterate based on user feedback
   - *Feature Priority*: MVP features that prove value over polished edge cases

5. **Transparency builds trust** - Show operators exactly what we're doing
   - *Code Impact*: Clear explanations of AI analysis, no "black box" results
   - *Feature Priority*: Privacy controls and data visibility features

## Design Philosophy (Palantir-Inspired)

### Core Principles
- **Data Density with Clarity**: Show complex insights through simple visualizations
- **Progressive Disclosure**: Surface information as operators need it
- **Actionable Intelligence**: Every insight must suggest clear next steps
- **Trust Through Transparency**: Show how AI conclusions are reached

### Visual Language
```css
/* Brand Colors - Reflect trust and sophistication */
--primary-dark: #03202F;    /* Trust, depth */
--primary-teal: #2DD4BF;    /* Innovation, clarity */
--automation-high: #10B981; /* Green - High potential */
--automation-medium: #F59E0B; /* Amber - Medium potential */
--automation-low: #6B7280;  /* Gray - Low potential */
```

### Interaction Patterns
- Hover reveals additional context (like Palantir's data exploration)
- Click for detailed analysis (drill-down capability)
- Clear visual hierarchy (most important insights prominent)
- Loading states that build confidence (show progress, set expectations)

## Strategic Evolution (3-Layer Platform Vision)

### Layer 1: Observation Infrastructure (MVP Focus - Weeks 1-4)
- **What**: Intelligent screen recording that captures how operators actually work
- **Why**: You can't improve what you can't see
- **How**: Non-invasive monitoring that respects privacy while capturing workflows
- **Development Focus**: Recording reliability, frame selection, basic analysis

### Layer 2: Translation Engine (Month 2-3)
- **What**: AI that converts operational patterns into technical specifications
- **Why**: Bridges the language gap between operations and engineering
- **How**: Pattern recognition + logistics domain knowledge + specification generation
- **Development Focus**: Advanced AI models, pattern libraries, spec generation

### Layer 3: Implementation Accelerator (Month 4-6)
- **What**: Tools and services that turn specs into working automation
- **Why**: Insights without action are worthless
- **How**: Both self-serve tools and done-for-you services
- **Development Focus**: Integration APIs, automation templates, service marketplace

## Success Metrics & Long-term Vision

### Year 1 Goals (Guide Feature Prioritization)
- **30 total customers** (target 50/50 split between direct platform and pilot paths)
- **$1M ARR** (platform subscriptions + implementation services)
- **100,000 operator hours saved monthly** (validate core value proposition)
- **Prove dual acquisition model** with clear metrics on both paths

### Year 3 Vision (Architecture Decisions)
- **Mission achieved**: 1,000,000 hours saved monthly
- **100+ active platform customers** (scalability requirements)
- **$10M+ ARR** with 60% from recurring platform fees (unit economics focus)
- **Equal mix of direct vs pilot-originated customers** (business model validation)

### Year 5 Ambition (Technology Evolution)
- **Platform for all operational intelligence** (beyond logistics)
- **$50M+ ARR** (IPO-ready business metrics)
- **Every logistics company knows NewSystem.AI** (market leadership)

## Founder's Why & Company Mission

Having worked at Flexport and in third-party logistics, I've lived this problem. I've watched brilliant operators spend hours on mindless copy-paste work. I've seen million-dollar automation projects fail because they were built on assumptions, not reality.

**Our Promise to Customers** (Guide All Development):
- We'll never sell theoretical solutions
- We'll show ROI before asking for major investment
- We'll make operators' lives better, not harder
- We'll be honest about what can and can't be automated
- We'll stay until the automation actually works

**This means in code**:
- Every feature must demonstrate clear value to operators
- Every AI insight must be actionable, not theoretical
- Every user interaction must build trust through transparency
- Every business model feature must support our dual-path strategy

## Complete Project Structure

```
NSAI_MVP/
├── frontend/                     # React + Vite application
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/          # Shared UI components
│   │   │   ├── ui/             # Basic UI elements (Button, Card, etc.)
│   │   │   ├── layout/         # Layout components (Header, Sidebar)
│   │   │   └── forms/          # Form components
│   │   ├── features/           # Feature-based organization
│   │   │   ├── auth/          # Authentication
│   │   │   │   ├── components/
│   │   │   │   ├── hooks/
│   │   │   │   └── services/
│   │   │   ├── recording/     # Screen recording functionality
│   │   │   │   ├── components/
│   │   │   │   │   ├── RecordingDashboard.tsx
│   │   │   │   │   ├── RecordingControls.tsx
│   │   │   │   │   ├── PermissionDialog.tsx
│   │   │   │   │   └── PrivacySettings.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   ├── useScreenRecording.ts
│   │   │   │   │   └── useRecordingUpload.ts
│   │   │   │   └── services/
│   │   │   │       └── recordingAPI.ts
│   │   │   ├── analysis/      # Analysis results display
│   │   │   │   ├── components/
│   │   │   │   │   ├── AnalysisTimeline.tsx
│   │   │   │   │   ├── ProcessingStatus.tsx
│   │   │   │   │   └── FrameViewer.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useAnalysisStatus.ts
│   │   │   │   └── services/
│   │   │   │       └── analysisAPI.ts
│   │   │   ├── results/       # Results dashboard and reports
│   │   │   │   ├── components/
│   │   │   │   │   ├── ResultsPage.tsx
│   │   │   │   │   ├── WorkflowFlowChart.tsx
│   │   │   │   │   ├── CostAnalysisCard.tsx
│   │   │   │   │   ├── RecommendationsList.tsx
│   │   │   │   │   └── PDFDownloadButton.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useResultsData.ts
│   │   │   │   └── services/
│   │   │   │       ├── pdfGenerator.ts
│   │   │   │       └── resultsAPI.ts
│   │   │   └── insights/      # ROI calculations and recommendations
│   │   │       ├── components/
│   │   │       │   ├── ROICalculator.tsx
│   │   │       │   ├── AutomationMatrix.tsx
│   │   │       │   └── SavingsProjection.tsx
│   │   │       ├── hooks/
│   │   │       │   └── useROICalculation.ts
│   │   │       └── services/
│   │   │           └── insightsAPI.ts
│   │   ├── lib/               # Shared utilities
│   │   │   ├── api-client.ts  # Axios configuration
│   │   │   ├── utils.ts       # Helper functions
│   │   │   ├── constants.ts   # App constants
│   │   │   └── types.ts       # TypeScript definitions
│   │   ├── styles/            # Global styles
│   │   │   ├── globals.css
│   │   │   └── components.css
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── .env.example
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── deps.py        # Dependencies
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py    # Authentication endpoints
│   │   │       ├── recordings.py  # Recording CRUD
│   │   │       ├── analysis.py    # Analysis orchestration
│   │   │       ├── results.py     # Results API
│   │   │       └── insights.py    # Business intelligence
│   │   ├── core/              # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py      # Settings
│   │   │   ├── security.py    # Auth/encryption
│   │   │   └── database.py    # Database connection
│   │   ├── models/            # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── recording.py
│   │   │   ├── analysis.py
│   │   │   └── insight.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── recording.py
│   │   │   ├── analysis.py
│   │   │   └── insight.py
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── recording/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── capture.py      # Recording management
│   │   │   │   ├── storage.py      # Video storage
│   │   │   │   └── privacy.py      # Privacy processing
│   │   │   ├── analysis/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestrator.py # Analysis pipeline
│   │   │   │   ├── frame_extractor.py
│   │   │   │   ├── gpt4v_client.py
│   │   │   │   └── result_parser.py
│   │   │   ├── insights/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── roi_calculator.py
│   │   │   │   ├── pattern_detector.py
│   │   │   │   └── report_generator.py
│   │   │   └── visualization/
│   │   │       ├── __init__.py
│   │   │       ├── flow_chart_builder.py
│   │   │       └── cost_analyzer.py
│   │   ├── utils/             # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── logging.py
│   │   │   └── helpers.py
│   │   ├── background/        # Background tasks
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py       # Celery tasks
│   │   │   └── scheduler.py   # Periodic jobs
│   │   └── main.py            # FastAPI app
│   ├── tests/                 # Test files
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_models/
│   ├── alembic/               # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── docs/                      # Documentation
│   ├── api/                   # API documentation
│   ├── deployment/            # Deployment guides
│   └── development/           # Development guides
├── .github/
│   └── workflows/
│       ├── frontend-ci.yml
│       └── backend-ci.yml
├── .gitignore
├── README.md
├── docker-compose.yml         # Local development
└── railway.toml              # Railway deployment config
```

## Tech Stack Details

### Frontend (React + Vite + TypeScript)
```json
// package.json dependencies
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "@supabase/supabase-js": "^2.7.0",
    "tailwindcss": "^3.2.0",
    "react-flow-renderer": "^11.5.0",  // Flow charts
    "@react-pdf/renderer": "^3.1.0",   // PDF generation
    "framer-motion": "^9.0.0",         // Animations
    "lucide-react": "^0.105.0"         // Icons
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0",
    "typescript": "^4.9.0",
    "@types/react": "^18.0.0",
    "vitest": "^0.28.0",
    "@testing-library/react": "^13.4.0",
    "eslint": "^8.34.0",
    "prettier": "^2.8.0"
  }
}
```

### Backend (FastAPI + Python)
```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.89.0"
uvicorn = {extras = ["standard"], version = "^0.20.0"}
supabase = "^1.0.0"
openai = "^0.26.0"
sqlalchemy = "^2.0.0"
alembic = "^1.9.0"
pydantic = {extras = ["email"], version = "^1.10.0"}
python-multipart = "^0.0.5"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
celery = "^5.2.0"
redis = "^4.5.0"
opencv-python = "^4.7.0"
pillow = "^9.4.0"
pytest = "^7.2.0"
httpx = "^0.23.0"

[tool.poetry.group.dev.dependencies]
pytest-asyncio = "^0.20.0"
black = "^22.12.0"
isort = "^5.12.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
```

## Database Schema

### Core Tables
```sql
-- Users and Organizations
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    organization_id UUID,
    role VARCHAR(50) DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) DEFAULT 'starter', -- starter, growth, enterprise
    billing_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recording Management
CREATE TABLE recordings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'recording', -- recording, processing, completed, failed
    duration_seconds INTEGER,
    file_path TEXT,
    file_size_bytes BIGINT,
    metadata JSONB DEFAULT '{}',
    privacy_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    INDEX idx_recordings_user_status (user_id, status),
    INDEX idx_recordings_created (created_at DESC)
);

-- Analysis Results
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recording_id UUID REFERENCES recordings(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'queued', -- queued, processing, completed, failed
    gpt_version VARCHAR(50) DEFAULT 'gpt-4-vision-preview',
    frame_count INTEGER,
    processing_time_seconds INTEGER,
    processing_cost DECIMAL(8,4),
    insights JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    INDEX idx_analysis_recording (recording_id),
    INDEX idx_analysis_status (status)
);

-- Automation Opportunities
CREATE TABLE automation_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    workflow_type VARCHAR(100) NOT NULL, -- email_to_wms, excel_reporting, etc.
    priority VARCHAR(20) DEFAULT 'medium', -- high, medium, low
    time_saved_weekly_hours DECIMAL(5,2),
    implementation_complexity VARCHAR(50), -- quick_win, strategic, consider, defer
    roi_score DECIMAL(5,2),
    automation_potential DECIMAL(3,2), -- 0.0 to 1.0
    description TEXT,
    recommendations TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_opportunities_analysis (analysis_id),
    INDEX idx_opportunities_priority (priority, roi_score DESC)
);

-- Workflow Visualizations
CREATE TABLE workflow_visualizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    flow_chart_data JSONB NOT NULL, -- nodes, edges, layout
    thumbnail_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cost Analysis
CREATE TABLE cost_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    current_monthly_cost DECIMAL(10,2),
    projected_monthly_cost DECIMAL(10,2),
    implementation_cost DECIMAL(10,2),
    payback_period_days INTEGER,
    annual_savings DECIMAL(12,2),
    cost_breakdown JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generated Reports
CREATE TABLE generated_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL, -- pdf, excel, shareable_link
    file_url TEXT,
    access_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_reports_token (access_token),
    INDEX idx_reports_expires (expires_at)
);
```

## API Endpoints Structure

### Authentication
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

### Recording Management
```
POST   /api/v1/recordings/start          # Start new recording
POST   /api/v1/recordings/{id}/chunks    # Upload video chunks
POST   /api/v1/recordings/{id}/complete  # Mark recording complete
GET    /api/v1/recordings                # List user recordings
GET    /api/v1/recordings/{id}           # Get recording details
DELETE /api/v1/recordings/{id}           # Delete recording
PUT    /api/v1/recordings/{id}/privacy   # Update privacy settings
```

### Analysis Pipeline
```
POST   /api/v1/analysis/{recording_id}/start  # Start analysis
GET    /api/v1/analysis/{id}/status           # Get analysis status
GET    /api/v1/analysis/{id}/results          # Get analysis results
POST   /api/v1/analysis/{id}/retry            # Retry failed analysis
```

### Results & Insights
```
GET    /api/v1/results/{session_id}           # Complete results data
GET    /api/v1/results/{session_id}/summary   # Executive summary
GET    /api/v1/results/{session_id}/flow      # Flow chart data
GET    /api/v1/results/{session_id}/opportunities  # Automation opportunities
GET    /api/v1/results/{session_id}/cost      # Cost analysis
POST   /api/v1/results/{session_id}/pdf       # Generate PDF report
POST   /api/v1/results/{session_id}/share     # Create shareable link
```

### Dashboard & Analytics
```
GET    /api/v1/dashboard/overview          # User dashboard data
GET    /api/v1/analytics/usage             # Usage statistics
GET    /api/v1/analytics/savings           # Savings metrics
```

## Environment Variables

### Frontend (.env.example)
```bash
# Application
VITE_APP_NAME=NewSystem.AI
VITE_APP_ENV=development

# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_VERSION=v1

# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_PDF_GENERATION=true
VITE_MAX_RECORDING_DURATION=1800  # 30 minutes

# External Services
VITE_SENTRY_DSN=https://your-sentry-dsn
```

### Backend (.env.example)
```bash
# Application
APP_NAME=NewSystem.AI API
APP_ENV=development
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://user:password@localhost/newsystem_db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI Services
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_ORG_ID=your-org-id
GPT4V_MODEL=gpt-4-vision-preview
MAX_TOKENS_PER_REQUEST=4096

# Storage
SUPABASE_STORAGE_BUCKET=recordings
MAX_FILE_SIZE_MB=500
ALLOWED_VIDEO_FORMATS=webm,mp4

# Background Jobs
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# External Services
SENTRY_DSN=https://your-sentry-dsn
LOGGING_LEVEL=INFO

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,https://app.newsystem.ai

# Business Logic
DEFAULT_ANALYSIS_TIMEOUT_MINUTES=10
MAX_CONCURRENT_ANALYSES=5
COST_PER_GPT4V_REQUEST=0.01
```

## Development Commands

### Frontend Commands
```bash
# Development
npm run dev              # Start dev server (localhost:3000)
npm run build            # Production build
npm run preview          # Preview production build
npm run lint             # ESLint check
npm run lint:fix         # Fix ESLint issues
npm run test             # Run unit tests (Vitest)
npm run test:ui          # Visual test runner
npm run test:coverage    # Test coverage report
npm run type-check       # TypeScript type checking

# Dependencies
npm install              # Install dependencies
npm update               # Update dependencies
npm audit                # Security audit
```

### Backend Commands  
```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Dev server
python -m app.main       # Alternative dev server start

# Database
alembic upgrade head     # Run migrations
alembic revision --autogenerate -m "Description"  # Create migration
python -c "from app.core.database import create_tables; create_tables()"  # Create tables

# Testing
pytest                   # Run all tests
pytest tests/test_api/   # Run API tests only
pytest --cov=app         # Run tests with coverage
pytest -v -s             # Verbose output
pytest --cov-report=html # HTML coverage report

# Code Quality
black .                  # Format code
isort .                  # Sort imports
flake8                   # Linting
mypy app/                # Type checking

# Background Jobs
celery -A app.background.tasks worker --loglevel=info  # Start worker
celery -A app.background.tasks beat --loglevel=info    # Start scheduler
celery -A app.background.tasks flower                  # Monitoring UI

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker  # Production server
```

### Docker Commands
```bash
# Development
docker-compose up -d              # Start all services
docker-compose up --build        # Rebuild and start
docker-compose down               # Stop all services
docker-compose logs backend      # View backend logs

# Production
docker build -t newsystem-api .  # Build production image
docker run -p 8000:8000 newsystem-api  # Run production container
```

## Deployment Configuration

### Railway Configuration (railway.toml)
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "backend/Dockerfile"

[deploy]
numReplicas = 2
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[environments.production]
[environments.production.variables]
APP_ENV = "production"
DEBUG = "false"

[environments.production.plugins]
[[environments.production.plugins]]
name = "postgresql"
[[environments.production.plugins]]
name = "redis"
```

### GitHub Actions CI/CD
```yaml
# .github/workflows/backend-ci.yml
name: Backend CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Testing Strategy

### Frontend Testing (Vitest + Testing Library)
```typescript
// Example test structure
describe('RecordingControls', () => {
  it('should start recording when permission granted', async () => {
    // Mock MediaRecorder API
    // Test recording flow
    // Assert state changes
  });

  it('should handle permission denied gracefully', async () => {
    // Mock permission denial
    // Test error handling
    // Assert error messaging
  });
});
```

### Backend Testing (Pytest + FastAPI TestClient)
```python
# Example test structure
class TestRecordingAPI:
    def test_start_recording_success(self, client, auth_headers):
        response = client.post(
            "/api/v1/recordings/start",
            json={"title": "Test Recording"},
            headers=auth_headers
        )
        assert response.status_code == 201
        assert response.json()["status"] == "recording"

    def test_analysis_pipeline_integration(self, client, sample_recording):
        # Test full analysis flow
        # Mock GPT-4V responses
        # Assert results structure
        pass
```

### Test Coverage Targets
- **Unit Tests**: 80% coverage minimum
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user flows (recording → analysis → results)
- **Performance Tests**: 100 concurrent users, response time < 200ms

## Development Approach

### MVP Scope (30-day timeline)
1. **Week 1**: Screen recording with chunked upload
2. **Week 2**: GPT-4V analysis pipeline
3. **Week 3**: Results dashboard with ROI calculations
4. **Week 4**: Polish and deployment

### Key Features (Aligned with Business Strategy)
- Web-based screen recording (2 FPS, 5-second chunks)
- Smart frame selection for GPT-4V analysis (cost optimization)
- Workflow pattern recognition (focus on email → WMS wedge)
- Automation opportunity identification (support both business paths)
- ROI reporting with cost-benefit analysis (prove value for pilots)
- PDF report generation (shareable with decision makers)
- Interactive flow chart visualization (Palantir-inspired clarity)

### Business-Critical Implementation Notes
- **Support dual business model**: API design must support both platform direct and pilot workflows
- **Focus on email → WMS wedge**: Prioritize detection and analysis of this specific pattern
- **Cost consciousness**: GPT-4V optimization is critical for unit economics
- **Trust building**: Always show confidence scores and explain AI reasoning

## Current Status

This repository contains architectural documentation and planning files in `.cursor/rules/`. The actual implementation has not yet begun. All development should start from scratch following the architecture defined in:

- `newsystem-vision-doc.mdc` - Company vision and strategy
- `august-mvp-plan.mdc` - 30-day development roadmap  
- `newsystem-mvp-architecture.mdc` - Technical architecture specification

## Key Constraints

- **Timeline**: 30-day MVP delivery
- **Scale**: Support 100 concurrent users
- **Budget**: ~$500/month infrastructure costs
- **Focus**: Logistics/warehouse operations (email → WMS wedge)
- **Privacy**: Built-in PII detection and user controls
- **Business Model**: Must support both platform direct and pilot workflows

## Important Notes for Developers

- **Business Context First**: Every feature decision should align with our mission of saving 1M operator hours monthly
- **Dual Business Model**: Architecture must support both platform direct ($2.5K-5K/month) and pilot programs ($15K/4 weeks)
- **Cost Optimization Critical**: GPT-4V API costs directly impact unit economics - optimize frame selection and batching
- **Operator-Centric Design**: UI/UX should speak to logistics coordinators, not IT departments
- **Email → WMS Focus**: This is our wedge - prioritize detection and analysis of this specific workflow pattern
- **Trust Through Transparency**: Always show confidence scores, explain AI reasoning, provide privacy controls
- **Reality Over Theory**: Build for observed workflows, not theoretical optimizations
- **Speed Over Perfection**: Ship 80% solutions quickly, iterate based on user feedback

Remember: We're not just building software - we're building the bridge between operational expertise and technical implementation that will save millions of hours of human work.