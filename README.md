# NewSystem.AI MVP

**Mission: Save 1,000,000 operator hours monthly through intelligent workflow analysis and automation discovery.**

NewSystem.AI is an AI-powered screen recording and workflow analysis platform that helps logistics companies identify automation opportunities. We capture how operators actually work, analyze patterns with GPT-4V, and provide actionable ROI-driven automation recommendations.

## 🚀 Quick Start

### Development Environment
```bash
# Clone and start everything
git clone git@github.com:toinevv/NSAI_MVP.git
cd NSAI_MVP
./start-dev.sh
```

**Services will be available at:**
- 📱 Frontend: http://localhost:5173
- 🔧 Backend: http://localhost:8000  
- 📚 API Docs: http://localhost:8000/docs

### Production Deployment
Deploy to Railway with one click:
```bash
railway up
```

## 🏗️ Architecture

### 3-Layer Platform Vision
1. **Layer 1: Observation Infrastructure** - Screen recording that captures operator workflows
2. **Layer 2: Translation Engine** - GPT-4V analysis converting patterns to technical specs  
3. **Layer 3: Implementation Accelerator** - Tools turning insights into working automation

### Tech Stack
- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL via Supabase
- **AI**: OpenAI GPT-4V for workflow analysis
- **Storage**: Supabase Storage for video files
- **Deployment**: Railway

## 🎯 Business Model

### Dual-Path Go-to-Market
- **Platform Direct**: $2,500-5,000/month for immediate access
- **Pilot Program**: $15K/4 weeks with 100% credit to annual contract

### Market Focus
- **Wedge**: Email → WMS data entry automation (15x daily, 2 min each)
- **Target**: Mid-size logistics companies (200-300 employees) 
- **Geographic**: Benelux → US → Global expansion

## 📊 Development Roadmap

### Week 1: Recording Foundation ✅
- [x] React + FastAPI foundation
- [x] Screen recording infrastructure
- [x] Chunked upload system
- [x] Database schema design

### Week 2: AI Analysis Pipeline
- [ ] GPT-4V integration
- [ ] Smart frame extraction
- [ ] Pattern recognition
- [ ] Cost tracking

### Week 3: Results & Insights  
- [ ] ROI calculations
- [ ] Flow chart visualization
- [ ] PDF report generation
- [ ] Shareable insights

### Week 4: Polish & Launch
- [ ] Error handling
- [ ] Performance optimization
- [ ] User testing
- [ ] Production deployment

## 🗄️ Database Schema

Logical, coherent structure supporting:
- **Multi-tenant organizations** with role-based access
- **Recording pipeline** with chunked upload reliability
- **AI analysis results** with cost tracking
- **Automation opportunities** with ROI calculations
- **Business intelligence** dashboards and reporting

See `database/README.md` for detailed schema documentation.

## 🔧 Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- OpenAI API key

### Environment Setup
1. Copy environment files:
   ```bash
   cp frontend/.env.example frontend/.env
   cp backend/.env.example backend/.env
   ```

2. Configure your credentials:
   - Supabase URL and keys
   - OpenAI API key
   - Database connection string

3. Apply database schema:
   - Run `database/supabase-schema.sql` in Supabase SQL Editor

### Development Commands
```bash
# Start both services
./start-dev.sh

# Frontend only
cd frontend && npm run dev

# Backend only  
cd backend && source venv/bin/activate && python -m app.main

# Database migrations
cd backend && alembic upgrade head
```

## 🔐 Security & Privacy

- **Row Level Security** on all database tables
- **PII detection** and masking capabilities
- **Organization-based** data isolation
- **Privacy controls** for screen recordings
- **Audit trails** for all operations

## 📈 Success Metrics

### Year 1 Goals
- 30 total customers (50/50 platform direct vs pilot)
- $1M ARR (platform + implementation services)
- 100,000 operator hours saved monthly
- Validate dual acquisition paths

### Long-term Vision
- **Year 3**: 1,000,000 hours saved monthly (mission achieved)
- **Year 5**: $50M+ ARR, IPO-ready metrics

## 🤝 Contributing

### Code Style
- **Frontend**: React functional components with TypeScript
- **Backend**: FastAPI async patterns with Pydantic models
- **Database**: PostgreSQL best practices with proper indexing

### Development Principles
1. **Operators are heroes** - Make their expertise visible
2. **Reality over theory** - Build for actual workflows  
3. **Speed over perfection** - Fast iterations beat planning
4. **Transparency builds trust** - Show AI reasoning clearly

## 📋 Project Structure

```
NSAI_MVP/
├── frontend/           # React + Vite application
├── backend/           # FastAPI application  
├── database/          # Schema and migrations
├── docs/             # Documentation
├── start-dev.sh      # Development startup script
└── railway.toml      # Production deployment config
```

## 📞 Support

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Development**: See `CLAUDE.md` for comprehensive guidance

---

**Built to transform logistics operations through intelligent automation discovery.**
*Saving 1,000,000 operator hours monthly.* 🚀
