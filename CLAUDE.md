# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Mission Statement

**To save 1,000,000 operator hours monthly by transforming how logistics companies capture, understand, and automate their operational workflows.**

## Development Commands

### Quick Start
```bash
# Start entire development environment
./start-dev.sh

# Access services at:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000  
# API Docs: http://localhost:8000/docs
```

### Individual Services
```bash
# Backend only
cd backend && source venv/bin/activate && python -m app.main

# Frontend only  
cd frontend && npm run dev

# Backend with auto-reload during development
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0
```

### Testing
```bash
# Run all backend tests
cd backend && python -m pytest tests/

# Run specific test file
cd backend && python -m pytest tests/test_unit.py -v

# Run integration tests
cd backend && python -m pytest tests/test_integration.py -v

# Test GPT-4V client configuration
cd backend && python tests/test_services/test_gpt4v_client_config.py
```

### Frontend Development
```bash
# Install dependencies
cd frontend && npm install

# Build for production
cd frontend && npm run build

# Lint frontend code
cd frontend && npm run lint

# Preview production build
cd frontend && npm run preview
```

### Database Operations (Supabase)
```bash
# Apply schema in Supabase SQL editor (recommended order):
# 1) database/supabase_migration_004_bulletproof.sql
# 2) database/supabase_migration_005_complete_multitenant.sql
# Or use database/current-schema.sql for a complete snapshot
```

## Architecture Overview

NewSystem.AI follows a **3-Layer Architecture** that transforms screen recordings into automation specifications:

### Layer 1: Observation Infrastructure
**Purpose**: Capture how operators actually work through privacy-first screen recording
- **Location**: `frontend/src/features/recording/`
- **Key Components**:
  - `RecordingControls.tsx` - Browser-based screen capture at 2 FPS
  - `uploadQueue.ts` - Chunked upload system (5-second chunks)
  - `sessionPersistence.ts` - Client-side state management
- **Database**: `recording_sessions`, `video_chunks` tables
- **Storage**: Supabase Storage for video files

### Layer 2: Translation Engine  
**Purpose**: AI-powered analysis converting screen patterns into technical specifications
- **Location**: `backend/app/services/analysis/`
- **Key Components**:
  - `orchestrator.py` - Main analysis coordinator and pipeline manager
  - `frame_extractor.py` - Extracts frames at 1 FPS from recordings (critical: fixed 93.5% frame loss bug)
  - `gpt4v_client.py` - OpenAI GPT-4o integration for visual workflow analysis
  - `prompts.py` - 17+ specialized prompts for different analysis types (natural, logistics, email_wms, etc.)
  - `result_parser.py` - Converts GPT-4o responses into structured data
- **Database**: `analysis_results`, `automation_opportunities` tables
- **Cost Optimization**: Uses "high detail" images, ~$0.10-0.60 per analysis

### Layer 3: Implementation Accelerator
**Purpose**: Transform analysis insights into actionable automation recommendations  
- **Location**: `frontend/src/features/analysis/components/`
- **Key Components**:
  - `MinimalResultsPage.tsx` - 4-tab results interface (Overview, Natural Language, Raw JSON, Workflow Chart)
  - `DynamicWorkflowChart.tsx` - Interactive flow visualization using ReactFlow
  - `RecordingsList.tsx` - Session management and analysis status
- **API Endpoints**: `/api/v1/results/` for serving processed analysis data
- **ROI Calculator**: `backend/app/services/insights/roi_calculator.py`

## Critical Architecture Patterns

### Frame Extraction Pipeline
The frame extraction system is **mission-critical** - a bug that lost 93.5% of frames was fixed in commit b255ea4:
- **Target**: 1 FPS extraction (optimal cost/insight balance)
- **Configuration**: No scene detection (UI workflows don't benefit)
- **Limits**: Maximum 120 frames (~$1.20) per analysis
- **Location**: `frame_extractor.py` - handle with extreme care

### GPT-4o Analysis Flow
1. **Input**: Recording → Frame Extraction (1 FPS)
2. **Processing**: GPT-4o with specialized prompts → Raw JSON response
3. **Parsing**: `result_parser.py` converts to structured insights
4. **Storage**: Both raw GPT response AND parsed results in database
5. **Frontend**: Multiple view formats (natural language, structured data, charts)

### Database Strategy
- **Pure Supabase PostgreSQL** with RLS and native API access
- **Zero ORM layer** - complete elimination of SQLAlchemy, application talks to Supabase directly
- **Multi-tenant architecture** via organization_id columns with application-level filtering

### API Architecture
```
/api/v1/recordings/     - CRUD operations for screen recordings
/api/v1/analysis/       - Trigger and monitor GPT-4V analysis  
/api/v1/results/        - Serve processed analysis results
/api/v1/results/{id}/raw - Raw GPT-4V responses for debugging
/api/v1/insights/       - ROI calculations and business metrics
```

## Business Context

### Target Market: Logistics Email→WMS Automation
- **Primary Use Case**: Operators manually copying data from emails into WMS systems
- **Frequency**: 15+ times daily, 2 minutes each = 30 minutes/day savings potential
- **Market**: Mid-size logistics companies (200-300 employees) in Benelux
- **Expansion**: Benelux → US → Global

### Dual Revenue Model
1. **Platform Direct**: $2,500-5,000/month for immediate access
2. **Pilot Program**: $15K/4 weeks with 100% credit to annual contract

## Development Principles

1. **Operators are heroes** - Make their expertise visible through AI analysis
2. **Reality over theory** - Capture actual workflows, not idealized processes  
3. **Speed over perfection** - Fast iterations with real customer feedback
4. **Transparency builds trust** - Show AI reasoning clearly in Natural Language tab

## Configuration Management

### Environment Setup
- **Backend**: `.env` file with Supabase URL/keys, OpenAI API key
- **Frontend**: `.env` file with Supabase public configuration
- **Development**: `start-dev.sh` handles virtual env creation and dependency installation

### Key Settings (`app/core/config.py`)
- `GPT4V_MODEL`: Currently "gpt-4o" 
- `GPT4V_IMAGE_DETAIL`: "high" for optimal analysis quality
- `CHUNK_SIZE_SECONDS`: 5 (recording upload chunks)
- `COST_PER_GPT4V_REQUEST`: $0.01 baseline cost estimation
- `DEFAULT_FRAMES_PER_SECOND`: 1.0 (1 FPS for cost-optimal analysis)
- `DEFAULT_MAX_FRAMES_PER_VIDEO`: 120 (maximum frames per analysis)

## Commit Guidelines

**Current instruction: "please commit after iterations of the mvp, we are rarely commiting now"**

When committing:
- Focus on substantial feature completions rather than incremental changes
- Include clear descriptions of business value/impact
- Always push to remote GitHub repository
- Use conventional commit format with emojis for visibility

## Production-Ready Status

**Current State: Production-ready MVP (January 2025)**
- ✅ **Pure Supabase architecture** - Complete elimination of SQLAlchemy
- ✅ **Multi-tenant support** via organization_id columns (RLS policies in migration files)
- ✅ **GPT-4o integration** with cost-optimized frame extraction 
- ✅ **Comprehensive error handling** and retry mechanisms throughout
- ✅ **Real data transparency** - No mock data, real analysis results or clear empty states
- ✅ **12-table database schema** supporting complex business workflows

**Key Implementation Insights:**
- **Frame extraction system is mission-critical** - handle `frame_extractor.py` with extreme care
- **Pure Supabase operations** - Zero ORM complexity, direct table operations throughout
- **Organization-based data isolation** - Multi-tenant via organization_id filtering
- **Privacy-first design** - Comprehensive controls, no audio recording, user-controlled blur

## Layer Documentation Reference

The project includes comprehensive architecture documentation:
- `Architecture/CURRENT_ARCHITECTURE.md` - Complete system architecture overview with actual implementation details
- `Architecture/LAYER_1_OBSERVATION_INFRASTRUCTURE.md` - Screen recording and data capture architectural vision
- `Architecture/LAYER_2_TRANSLATION_ENGINE.md` - AI analysis pipeline and GPT-4o integration architectural vision  
- `Architecture/LAYER_3_IMPLEMENTATION_ACCELERATOR.md` - Results visualization and ROI tools architectural vision

These documents provide architectural vision and current implementation status. The layer documents focus on architectural concepts rather than implementation code.