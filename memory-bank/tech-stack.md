# Tech Stack Recommendation: AI-Powered Fake News Detector

This document outlines a recommended technology stack for the AI-Powered Fake News Detector project, emphasizing simplicity and alignment with the project's goals.

## Recommended Tech Stack:

| Component                 | Technology                                               | Reason                                                                                                                                          |
| :------------------------ | :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**              | **HTML, CSS, JavaScript (Vanilla)**                      | Core web technologies, providing direct control over the UI without framework overhead. Suitable for straightforward user interfaces.           |
| **Backend API**           | **Python with FastAPI**                                  | High performance, easy to learn, with built-in data validation and API documentation. Excellent for Python-based AI/ML integrations.            |
| **LLM Integration**       | **Google Gemini API**                                    | Provides access to powerful language models from Google, with client libraries for easy integration, suitable for text analysis and generation. |
| **Database (Vector)**     | **ChromaDB**                                             | Open-source vector database, simple to integrate within Python. Ideal for storing text embeddings and performing semantic searches on claims.   |
| **Web Search API**        | **Google Custom Search JSON API / Bing Web Search API**  | Established APIs for programmatic web searching to gather information related to news claims.                                                   |
| **Trendiness API**        | **`pytrends` (unofficial Google Trends API for Python)** | Python library to access Google Trends data, useful for assessing the current discussion volume around a claim.                                 |
| **Credibility Scoring**   | **Custom Python Logic**                                  | Implemented within the FastAPI backend, allowing for flexible algorithms and integration with external fact-checking resources via `requests`.  |
| **Deployment**            | **Vercel**                                               | Supports deployment of static frontends (HTML/CSS/JS) and Python serverless functions (for FastAPI), offering a unified platform.               |
| **Task Queue (Optional)** | **Vercel Background Functions**                          | Can handle asynchronous, longer-running tasks within the Vercel ecosystem if needed.                                                            |

---

## Detailed Breakdown & Justification:

1.  **Frontend: HTML, CSS, JavaScript (Vanilla)**

    - Utilizes fundamental web technologies for building the user interface. This approach offers direct control and avoids the complexity of JavaScript frameworks, making it suitable for simpler UIs.
    - Vercel provides excellent support for deploying static sites built with these technologies.

2.  **Backend API: Python with FastAPI**

    - FastAPI is a modern, fast web framework for building APIs with Python. Its use of Python type hints for data validation and automatic API documentation (Swagger UI) simplifies development.
    - Well-suited for projects involving data processing and machine learning, given Python's extensive libraries.
    - Can be deployed as serverless functions on Vercel.

3.  **LLM Integration: Google Gemini API**

    - Leverages Google's Gemini models for advanced natural language understanding and generation tasks required for analyzing news claims.
    - Google provides Python client libraries, facilitating integration into the FastAPI backend.

4.  **Database (Vector): ChromaDB**

    - An open-source vector database designed for ease of use, particularly with Python. It's suitable for storing embeddings of news claims and performing similarity searches for the "Claim History" feature.
    - Can be run in-memory for development or persist data to disk.

5.  **Web Search API: Google Custom Search JSON API / Bing Web Search API**

    - These APIs allow the system to programmatically search the web for information related to the user's query, a key part of the information gathering process.

6.  **Trendiness API: `pytrends`**

    - An unofficial Python wrapper for Google Trends, allowing the application to fetch data on the search interest of specific terms, contributing to the "Trendiness" score.

7.  **Credibility Scoring: Custom Python Logic**

    - This component will involve developing custom algorithms in Python within the FastAPI backend. It will evaluate the trustworthiness of information, potentially by analyzing source data or integrating with external fact-checking services.

8.  **Deployment: Vercel**

    - Vercel offers a streamlined platform for deploying both the frontend (static HTML, CSS, JS files) and the backend (FastAPI as Python serverless functions). It provides features like CI/CD and a global CDN.

9.  **Task Queue (Optional): Vercel Background Functions**
    - For operations that might take longer than a standard API request (e.g., extensive data collection or processing), Vercel's Background Functions can be used to handle these tasks asynchronously without blocking the main API response.

This tech stack is designed to provide a functional and manageable foundation for the AI-Powered Fake News Detector project, aligning with the specified technology preferences.
