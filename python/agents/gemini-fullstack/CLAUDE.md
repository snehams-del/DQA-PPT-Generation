# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend Development
```bash
# Install dependencies (installs uv if not present)
make install

# Run backend API server
make dev-backend
# or: uv run adk api_server app --allow_origins="*"

# Run ADK web playground 
make playground
# or: uv run adk web --port 8501
```

### Frontend Development
```bash
# Run frontend development server
make dev-frontend
# or: npm --prefix frontend run dev

# Build frontend
npm --prefix frontend run build

# Lint frontend
npm --prefix frontend run lint
```

### Full Development
```bash
# Run both backend and frontend concurrently
make dev
```

### Code Quality
```bash
# Run all linting and formatting checks
make lint

# Individual tools:
uv run codespell          # Spell checking
uv run ruff check . --diff      # Linting
uv run ruff format . --check --diff  # Formatting
uv run mypy .             # Type checking
```

## Project Architecture

### High-Level Structure
This is a **fullstack research agent** built with Google's Agent Development Kit (ADK). It demonstrates a sophisticated, production-ready workflow that combines:

- **Backend**: ADK-powered FastAPI server with multi-agent research pipeline
- **Frontend**: React 19 + TypeScript + Vite with Tailwind CSS and Shadcn UI
- **Multi-phase workflow**: Human-in-the-loop planning + autonomous research execution

### Backend Architecture (`app/`)
The backend implements a **two-phase research workflow**:

**Phase 1: Interactive Planning**
- `interactive_planner_agent`: Generates research plan from user topic
- `plan_generator`: Creates structured research goals with tags
- Human-in-the-loop approval process

**Phase 2: Autonomous Research Pipeline**
- `section_planner`: Converts approved plan to report outline
- `section_researcher`: Iterative research with search and critique loop
- `enhanced_search_executor`: Executes web searches via Google Search
- `report_composer_with_citations`: Final report generation with citations

**Key Components**:
- `app/agent.py`: Multi-agent definitions and workflow orchestration
- `app/config.py`: ResearchConfiguration dataclass with model settings
- Uses `google-adk==1.4.2` with Gemini 2.5 models (pro for critic, flash for worker)

### Frontend Architecture (`frontend/`)
React application that integrates with the ADK backend:

**Core Components**:
- `ActivityTimeline.tsx`: Visual workflow progress tracking
- `ChatMessagesView.tsx`: Message display with research findings
- `InputForm.tsx`: User input handling
- `WelcomeScreen.tsx`: Initial interface

**Integration Points**:
- Connects to backend via agent names (e.g., `section_researcher`, `report_composer_with_citations`)
- Tracks research metrics (website counts, timeline updates)
- Handles different output types (planning vs research findings vs final reports)

### Agent Communication Flow
```
User Topic → interactive_planner_agent → [Human Approval] → 
section_planner → section_researcher + enhanced_search_executor → 
report_composer_with_citations → Final Report
```

## Configuration

### Environment Setup
Create `app/.env` with:
```bash
# For Google AI Studio
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_ai_studio_key

# For Google Cloud Vertex AI (default)
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=global
```

### Research Parameters
Modify `app/config.py` ResearchConfiguration:
- `critic_model`: Model for evaluation (default: "gemini-2.5-pro")
- `worker_model`: Model for generation (default: "gemini-2.5-flash")  
- `max_search_iterations`: Search loop limit (default: 5)

## Important Notes

### Agent Name Dependencies
The frontend expects specific agent names from `app/agent.py`:
- `section_researcher` & `enhanced_search_executor` → track websites consulted
- `report_composer_with_citations` → process final report
- `interactive_planner_agent` → update AI messages during planning
- `plan_generator` and `section_planner` → timeline labels

**If you rename agents in the backend, update corresponding references in the frontend code.**

### Technology Stack
- **Backend**: Google ADK 1.4.2, FastAPI, Gemini 2.5 models
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS 4.1.5, Shadcn UI
- **Tools**: uv for Python dependencies, ruff+mypy for linting, codespell for spell-checking
- **Python**: Requires 3.10-3.13