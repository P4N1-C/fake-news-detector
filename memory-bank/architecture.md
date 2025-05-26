# AI-Powered Fake News Detector - Architecture Documentation

## Overview

The AI-Powered Fake News Detector is a web-based application that uses Large Language Models (LLMs) and web search to analyze news claims for authenticity. The system follows a client-server architecture with a modern web frontend and a Python FastAPI backend.

## Project Structure

```
fake-news-detector/
├── .git/                    # Git repository metadata
├── .gitignore              # Git ignore rules
├── frontend/               # Frontend web application
│   ├── index.html         # Main HTML page
│   ├── style.css          # CSS styling
│   └── script.js          # JavaScript functionality
├── backend/                # Backend API server
│   ├── venv/              # Python virtual environment
│   ├── env.example        # Environment configuration template
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
└── memory-bank/           # Project documentation
    ├── architecture.md    # This file
    ├── design-documentation.md
    ├── implementation-plan.md
    ├── progress.md
    └── tech-stack.md
```

## Technology Stack

### Backend

- **Language:** Python 3.9+
- **Web Framework:** FastAPI 0.115.12
- **ASGI Server:** Uvicorn
- **Environment Management:** python-dotenv
- **Search Integration:** duckduckgo-search
- **Future:** Google Gemini API, ChromaDB

### Frontend

- **Languages:** HTML5, CSS3, JavaScript (ES6+)
- **Styling:** Modern CSS with glassmorphism design
- **Architecture:** Vanilla JavaScript (no frameworks)
- **Responsive:** Mobile-first design approach

### Development Tools

- **Version Control:** Git
- **Environment:** Python virtual environment
- **API Documentation:** FastAPI automatic Swagger UI

## System Architecture

### Current Implementation (Phase 0 - MVP Setup)

```
┌─────────────────┐     HTTP/JSON     ┌─────────────────┐
│   Frontend      │ ◄─────────────► │   Backend       │
│   (Browser)     │     API Calls     │   (FastAPI)     │
│                 │                   │                 │
│ • HTML UI       │                   │ • /health       │
│ • CSS Styling   │                   │ • CORS enabled  │
│ • JS Logic      │                   │ • Logging       │
└─────────────────┘                   └─────────────────┘
```

### Planned Full Architecture (Future Phases)

```
┌─────────────────┐     HTTP/JSON     ┌─────────────────┐
│   Frontend      │ ◄─────────────► │   Backend       │
│   (Browser)     │                   │   (FastAPI)     │
└─────────────────┘                   └─────┬───────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
          ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
          │   Web Search    │      │   LLM Service   │      │   Database      │
          │  (DuckDuckGo)   │      │ (Google Gemini) │      │   (ChromaDB)    │
          └─────────────────┘      └─────────────────┘      └─────────────────┘
```

## File Descriptions

### Frontend Files

#### `frontend/index.html`

**Purpose:** Main user interface for the application
**Key Features:**

- Responsive HTML5 structure
- News claim input textarea
- Results display sections (verdict, explanation)
- Loading indicators
- Feedback collection buttons
- Mobile-friendly viewport configuration

**Key Elements:**

- `#claimInput`: Text area for user input
- `#loadingIndicator`: Animated loading spinner
- `#resultsSection`: Container for analysis results
- `#feedbackSection`: User feedback collection

#### `frontend/style.css`

**Purpose:** Complete styling and visual design
**Key Features:**

- Modern glassmorphism design with backdrop blur effects
- Gradient backgrounds and smooth animations
- Responsive design with mobile breakpoints
- Interactive button states and hover effects
- Professional color scheme and typography

**Design Principles:**

- Mobile-first responsive approach
- Accessibility-friendly color contrasts
- Smooth transitions and micro-interactions
- Clean, professional appearance

#### `frontend/script.js`

**Purpose:** Client-side application logic and API communication
**Key Features:**

- DOM manipulation and event handling
- API communication with backend (future implementation)
- Loading state management
- Error handling and user feedback
- Form validation and input processing

**Key Functions:**

- `handleAnalyzeClaim()`: Processes claim analysis requests
- `handleFeedback()`: Manages user feedback submission
- `setLoadingState()`: Controls UI loading indicators
- `showResults()` / `hideResults()`: Result display management

### Backend Files

#### `backend/main.py`

**Purpose:** FastAPI application entry point and API endpoint definitions
**Key Features:**

- FastAPI application initialization
- CORS middleware configuration for cross-origin requests
- Logging configuration for debugging and monitoring
- Health check endpoint for system status

**Current Endpoints:**

- `GET /health`: Returns `{"status": "ok"}` for health monitoring

**Architecture Patterns:**

- Async/await support for concurrent request handling
- Environment variable loading with python-dotenv
- Structured logging for debugging
- Comprehensive error handling framework

#### `backend/requirements.txt`

**Purpose:** Python dependency management
**Key Dependencies:**

- `fastapi==0.115.12`: Web framework
- `uvicorn`: ASGI server
- `python-dotenv`: Environment variable management
- `duckduckgo-search==8.0.2`: Web search capabilities
- Supporting libraries for HTTP, JSON, and async operations

#### `backend/env.example`

**Purpose:** Environment configuration template
**Key Variables:**

- `GOOGLE_API_KEY`: For Gemini LLM integration
- `DEBUG`: Development/production mode flag
- `LOG_LEVEL`: Logging verbosity control
- Future API keys for enhanced search capabilities

### Configuration Files

#### `.gitignore`

**Purpose:** Version control exclusions
**Key Exclusions:**

- Environment files (`.env`)
- Python cache files (`__pycache__/`)
- Virtual environments (`venv/`)
- Database files (`chroma_db_data/`)
- IDE configurations and temporary files

## API Design

### Current API Specification

```yaml
openapi: 3.0.0
info:
  title: AI-Powered Fake News Detector
  version: 1.0.0

paths:
  /health:
    get:
      summary: Health check endpoint
      responses:
        200:
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "ok"
```

### Planned API Endpoints (Future Phases)

- `POST /analyze_claim`: Submit claim for analysis
- `POST /submit_feedback`: Submit user feedback
- `GET /claim_history`: Retrieve analysis history

## Data Flow

### Current Implementation

1. User opens `frontend/index.html` in browser
2. JavaScript loads and initializes event handlers
3. User interface renders with CSS styling
4. Backend can be started independently for health checks

### Planned Full Flow

1. User enters news claim in frontend
2. Frontend sends claim to backend API
3. Backend searches web for related information
4. Backend queries LLM for analysis
5. Backend stores result in vector database
6. Frontend displays verdict and explanation
7. User provides feedback, stored for future improvements

## Security Considerations

### Current Implementation

- CORS configured for development (broad permissions)
- Environment variables for sensitive configuration
- Basic input validation on frontend

### Future Enhancements

- API rate limiting
- Input sanitization and validation
- Secure API key management
- Production CORS restrictions
- Request authentication

## Development Workflow

### Setting Up Development Environment

1. Clone repository
2. Navigate to `backend/` directory
3. Activate virtual environment: `.\venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `env.example` to `.env` and configure
6. Start server: `python -m uvicorn main:app --reload`
7. Open `frontend/index.html` in browser

### Adding New Features

1. Backend: Add endpoints to `main.py`
2. Frontend: Update JavaScript for API calls
3. Update documentation in `memory-bank/`
4. Test thoroughly before committing

## Performance Considerations

### Current Optimizations

- Lightweight vanilla JavaScript (no framework overhead)
- Efficient CSS with minimal dependencies
- FastAPI's high-performance async architecture
- Modern browser APIs for optimal user experience

### Future Optimizations

- Database indexing for claim history
- Caching frequently analyzed claims
- Async web search processing
- CDN for static assets

## Monitoring and Logging

### Current Logging

- Python logging configuration in `main.py`
- Console logging for development
- Error tracking for debugging

### Future Enhancements

- Structured logging with timestamps
- Performance metrics collection
- User interaction analytics
- System health monitoring

This architecture provides a solid foundation for the fake news detection system while maintaining flexibility for future enhancements and scalability.
