# 🚀 Frontend-Backend Integration Demo Guide

## Overview

The AI-Powered Fake News Detector now has a fully integrated frontend and backend system with the complete fact-checking pipeline:

1. **Web Search** - Gathers evidence from the internet
2. **LLM Analysis** - Uses Google Gemini AI to analyze claims
3. **Verdict Generation** - Provides "Likely True", "Likely False", or "Uncertain" verdicts
4. **Interactive UI** - Clean, modern interface for testing

## Quick Start

### 1. Start the Backend Server

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Open the Frontend

```powershell
# Open frontend/index.html in your browser
Start-Process "frontend/index.html"
```

## Demo Test Cases

Try these sample claims to see the system in action:

### ✅ True Claims

- "The Earth orbits around the Sun"
- "Water boils at 100 degrees Celsius at sea level"
- "Apple is a technology company"

### ❌ False Claims

- "Climate change is a hoax created by scientists"
- "Unicorns were discovered in Montana yesterday"
- "The Moon is made of cheese"

### ⚠️ Uncertain Claims

- "A cure for cancer will be discovered next year"
- "Aliens visited Earth last week"
- "" (empty claim)

## What You'll See

1. **Loading State** - Animated spinner while processing (2-4 seconds)
2. **Verdict Display** - Color-coded verdict:
   - 🟢 Green for "Likely True"
   - 🔴 Red for "Likely False"
   - 🟡 Orange for "Uncertain/Needs More Info"
   - 🟣 Purple for "Error"
3. **Detailed Explanation** - AI-generated reasoning
4. **Search Results** - Sources used for analysis (up to 3 results)

## Features Implemented

### Backend

- ✅ FastAPI REST API
- ✅ Web search using DuckDuckGo
- ✅ Google Gemini LLM integration
- ✅ Comprehensive error handling
- ✅ Detailed logging

### Frontend

- ✅ Modern, responsive UI
- ✅ Real-time backend communication
- ✅ Loading states and error handling
- ✅ Color-coded verdict display
- ✅ Search results visualization
- ✅ Mobile-friendly design

## API Endpoint

**POST** `/analyze_claim`

**Request:**

```json
{
  "claim_text": "Your news claim here"
}
```

**Response:**

```json
{
  "received_claim": "Your news claim here",
  "search_results": [
    {
      "title": "Article title",
      "snippet": "Article content snippet"
    }
  ],
  "verdict": "Likely True/False/Uncertain/Needs More Info",
  "explanation": "Detailed AI analysis and reasoning"
}
```

## Performance

- **Average Response Time**: 2-4 seconds
- **Search Results**: 3 web sources per analysis
- **Rate Limiting**: Uses free Google Gemini API tier
- **Error Handling**: Graceful degradation for failed requests

## Next Steps

After testing and validation, the system is ready for **Phase 3: Database Integration** which will add:

- Claim history storage
- Duplicate detection
- Performance improvements
- Persistent storage with ChromaDB

---

**Ready for demo! 🎉**
