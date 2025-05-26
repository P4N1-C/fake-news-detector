# AI-Powered Fake News Detector: Implementation Plan (MVP) - No Code Version

This document outlines the step-by-step instructions for AI developers to implement the Minimum Viable Product (MVP) of the AI-Powered Fake News Detector. The focus is on establishing the core workflow using web search first, with database integration as a temporary storage solution before full database implementation later.

**Developer Guidelines:**

- Commit changes to Git frequently with clear, descriptive messages.
- Adhere to Python coding standards and project-specific style guides.
- Use environment variables for API keys and sensitive configurations.
- Log all errors for easier debugging.
- Implement error handling with appropriate timeout configurations.
- Update `architecture.md` and `progress.md` as you start working on the project.
- Refer to `design-documentation.md` for overall project context and `tech-stack.md` for technology choices.
- **Note:** Database storage is temporary for MVP - focus on creating a working detector using web search. Full database implementation will come later.

---

## Phase 0: Project Setup & Basic API

**Objective:** Initialize the project structure and a basic backend API endpoint.

1.  **Step 0.1: Project Directory and Git Initialization**

    - **Instruction:** Create the main project directory. Inside it, create `frontend/` and `backend/` subdirectories. Initialize a Git repository in the main project directory.
    - **Test:**
      - Verify that `git status` in the project root shows the `frontend/` and `backend/` directories as untracked.
      - Confirm the directory structure (`fake-news-detector/` containing `backend/` and `frontend/`) is correct.

2.  **Step 0.2: Backend Python Environment Setup**

    - **Instruction:** Navigate into the `backend/` directory. Create a Python virtual environment. Activate the virtual environment. Install `fastapi` and `uvicorn` (with standard ASGI server features) using `pip`. Create a `requirements.txt` file listing all installed dependencies with their versions.
    - **Test:**
      - Execute `pip freeze` within the activated virtual environment. Verify that `fastapi` and `uvicorn` are listed in the output.
      - Verify that `requirements.txt` exists and contains the installed packages with version numbers.

3.  **Step 0.3: Environment Configuration Setup**

    - **Instruction:** Create a `.env.example` file in the `backend/` directory. Document all required environment variables (e.g., `GOOGLE_API_KEY=your_gemini_api_key_here`). Add `.env` to `.gitignore` if it doesn't exist.
    - **Test:**
      - Verify that `.env.example` exists and documents the required environment variables.
      - Verify that `.env` is listed in `.gitignore`.

4.  **Step 0.4: Basic Backend Health Check Endpoint**

    - **Instruction:** In the `backend/` directory, create a `main.py` file. Implement a FastAPI application within this file. Define a GET endpoint at the path `/health` that returns a JSON response `{"status": "ok"}`. Add basic error logging configuration.
    - **Test:**
      - From the `backend/` directory, start the Uvicorn development server, pointing it to the FastAPI application in `main.py` and enabling auto-reload.
      - Open a web browser or use a tool like `curl` to send a GET request to `http://127.0.0.1:8000/health`.
      - Verify that the server responds with the JSON `{"status": "ok"}` and an HTTP status code of 200.

5.  **Step 0.5: Basic Frontend HTML Structure**

    - **Instruction:** In the `frontend/` directory, create `index.html`, `style.css`, and `script.js` files. In `index.html`, set up a basic HTML document structure including a title, a textarea for claim input, a button to submit the claim, designated `div` elements with unique IDs to display the verdict and explanation, and a loading indicator (initially hidden). Link the `style.css` and `script.js` files.
    - **Test:**
      - Open the `frontend/index.html` file directly in a web browser.
      - Verify that the page displays the title, the textarea input field, the submit button, placeholder areas for the verdict and explanation, and a loading indicator as defined by the HTML structure.

6.  **Step 0.6: Update Project Documentation**
    - **Instruction:** Populate `memory-bank/architecture.md` with the basic project structure and technology choices. Update `memory-bank/progress.md` to reflect Phase 0 completion.
    - **Test:**
      - Verify that both files contain relevant information about the current project state.

---

## Phase 1: Core Backend Logic - Information Gathering (Web Search)

**Objective:** Implement the API endpoint for claim submission and integrate basic web search functionality with error handling.

1.  **Step 1.1: API Endpoint for Claim Submission**

    - **Instruction:** In `backend/main.py`, define a Pydantic model to represent the structure of the claim submission request (expecting a `claim_text` string). Create a POST endpoint at `/analyze_claim` that accepts a JSON payload matching this Pydantic model. For this initial step, the endpoint should simply return a JSON response containing the `claim_text` it received. Add try-catch blocks and log any errors.
    - **Test:**
      - Ensure the Uvicorn server for the backend is running.
      - Use a tool like `curl` or Postman to send a POST request to `http://127.0.0.1:8000/analyze_claim`. The request body should be JSON (e.g., `{"claim_text": "Test news claim from API."}`).
      - Verify that the API responds with JSON containing the same claim text (e.g., `{"received_claim": "Test news claim from API."}`).

2.  **Step 1.2: Install Web Search Client Library**

    - **Instruction:** Within the activated backend virtual environment, install the `duckduckgo-search` Python library using `pip`. Update `requirements.txt` with the new dependency.
    - **Test:**
      - Execute `pip freeze`. Verify that `duckduckgo-search` is listed in the output.
      - Verify that `requirements.txt` is updated with the new dependency.

3.  **Step 1.3: Implement Web Search Utility Function**

    - **Instruction:** In the backend (either in `main.py` or a new utility file), create an asynchronous Python function named `search_web`. This function should accept a query string and an optional maximum number of results. It should use the `duckduckgo-search` library to perform a text search and return a list containing the top (e.g., 3) results, where each result is a dictionary containing its title and snippet/summary. Add error handling and logging for search failures.
    - **Test:**
      - Call the `search_web` function (e.g., from a temporary test route in FastAPI or by running it directly in a test Python script) with a sample search query (e.g., "current AI developments").
      - Verify that the function returns a list of dictionaries, and each dictionary contains non-empty 'title' and 'snippet' keys.
      - Test error handling by running the function without internet connection and verify that errors are logged.

4.  **Step 1.4: Integrate Web Search into Claim Analysis Endpoint**
    - **Instruction:** Modify the `/analyze_claim` POST endpoint in `backend/main.py`. When a claim is received, call the `search_web` function using the `claim_text` as the query. The endpoint should then return a JSON response containing both the original `received_claim` and the `search_results` obtained from the web search. Add comprehensive error handling and logging.
    - **Test:**
      - Send a POST request to the `/analyze_claim` endpoint with a sample news claim.
      - Verify that the JSON response includes the `received_claim` and a `search_results` key, where `search_results` is an array of objects, each having a title and snippet.
      - Test error scenarios and verify that appropriate error messages are logged.

---

## Phase 2: LLM Integration & Verdict Generation

**Objective:** Integrate Google Gemini API to analyze the claim and search results, generating a preliminary verdict with rate limiting considerations.

1.  **Step 2.1: Setup Google Gemini API Access and Library**

    - **Instruction:** Obtain a Google Gemini API key from the Google AI Studio or Google Cloud Console. Set this API key as an environment variable (e.g., `GOOGLE_API_KEY`) accessible to your backend application. Install the `google-generativeai` Python library using `pip`. Update `requirements.txt`. **Note:** Implement basic rate limiting awareness since using free Gemini API.
    - **Test:**
      - Execute `pip freeze`. Verify that `google-generativeai` is listed.
      - Verify `requirements.txt` is updated.
      - Create and run a small, separate Python script that attempts to configure the Gemini client using the API key from the environment variable and makes a simple generative query (e.g., "What is the capital of Canada?").
      - Verify that the script executes without authentication errors and successfully receives a plausible response from the Gemini API.

2.  **Step 2.2: Create LLM Verdict Generation Function**

    - **Instruction:** In the backend, create an asynchronous Python function (e.g., `get_llm_verdict`). This function should accept the news claim string and the list of search results (from Step 1.3). Inside the function:
      1.  Construct a detailed prompt for the Gemini model. The prompt should include the original news claim and a summarized version of the web search results.
      2.  Instruct the LLM to assess the likely truthfulness of the claim based _only_ on the provided information, to provide a verdict (e.g., "Likely True", "Likely False", "Uncertain/Needs More Info"), and a brief explanation for its verdict. Specify the desired response format (e.g., "Verdict: [Verdict] Explanation: [Explanation]").
      3.  Send this prompt to the Gemini API with appropriate timeout settings.
      4.  Parse the LLM's text response to extract the verdict and explanation.
      5.  Return a dictionary containing the extracted `verdict` and `explanation`.
      6.  Add comprehensive error handling and logging for API failures.
    - **Test:**
      - Call the `get_llm_verdict` function with a sample news claim and a list of mock search result dictionaries (each with 'title' and 'snippet').
      - Verify that the function returns a dictionary containing non-empty string values for both `verdict` and `explanation` keys, consistent with the expected output from the LLM.
      - Test error scenarios and verify proper logging.

3.  **Step 2.3: Integrate LLM Processing into Claim Analysis Endpoint**
    - **Instruction:** Modify the `/analyze_claim` POST endpoint in `backend/main.py`. After obtaining web search results (Step 1.4), call the `get_llm_verdict` function, passing it the original `claim_text` and the `search_results`. Include the `verdict` and `explanation` received from the LLM in the final JSON response of the API. Add comprehensive error handling for the entire pipeline.
    - **Test:**
      - Send a POST request to the `/analyze_claim` endpoint with a sample news claim.
      - Verify that the JSON response now includes `verdict` and `explanation` keys, and their values appear to be generated by the LLM based on the claim and (implicitly) the search results.
      - Test error scenarios throughout the pipeline.

---

## Phase 3: Database Integration - Claim History (Basic/Temporary)

**Objective:** Set up ChromaDB to store and retrieve processed claims for basic history checking. **Note:** This is temporary storage for MVP - full database implementation comes later.

1.  **Step 3.1: Install Vector Database Library**

    - **Instruction:** Within the activated backend virtual environment, install the `chromadb` Python library using `pip`. Update `requirements.txt`.
    - **Test:**
      - Execute `pip freeze`. Verify that `chromadb` is listed in the output.
      - Verify `requirements.txt` is updated.

2.  **Step 3.2: Initialize ChromaDB Client and Collection**

    - **Instruction:** In your backend code (e.g., `main.py` or a `db_utils.py` file), initialize a persistent ChromaDB client, specifying a local path for data storage (e.g., `./chroma_db_data`). Get or create a ChromaDB collection named `claims_history`. When creating the collection, specify an embedding function (e.g., `SentenceTransformerEmbeddingFunction` from `chromadb.utils.embedding_functions` using a model like "all-MiniLM-L6-v2"). Add error handling and logging for database operations.
    - **Test:**
      - Start the backend FastAPI application.
      - Verify that the specified data storage directory (e.g., `backend/chroma_db_data/`) is created in the file system and persists between sessions.
      - Check the application's console output for messages confirming successful initialization of the ChromaDB client and collection, or any error messages.

3.  **Step 3.3: Implement Claim History Check Function**

    - **Instruction:** Create an asynchronous Python function (e.g., `check_claim_history`) that accepts a `claim_text` string. Inside the function:
      1.  Generate a unique ID for the claim (e.g., an MD5 hash of the lowercased, stripped claim text).
      2.  Query the `claims_history` ChromaDB collection using this ID to retrieve any existing entry. Include `metadatas` and `documents` in the retrieval.
      3.  If an entry is found, extract and return relevant data (e.g., original claim text, stored verdict, explanation, and timestamp from metadata). If not found, return `None`.
      4.  Add error handling and logging for database query failures.
    - **Test:**
      - Call the `check_claim_history` function with a sample claim text.
      - Since the database is new/empty, verify that the function returns `None`.
      - Test error scenarios and verify proper logging.

4.  **Step 3.4: Implement Claim History Update Function**

    - **Instruction:** Create an asynchronous Python function (e.g., `update_claim_history`) that accepts the `claim_text`, `verdict`, and `explanation`. Inside the function:
      1.  Generate the same unique ID for the claim as in Step 3.3.
      2.  Create a metadata dictionary containing the `verdict`, `explanation`, and a current UTC timestamp.
      3.  Use the `upsert` method of the `claims_history` collection to add or update the claim. Store the `claim_text` as the document and the generated ID and metadata.
      4.  Add error handling and logging for database update failures.
    - **Test:**
      1.  Call the `update_claim_history` function with a sample claim text, a sample verdict, and a sample explanation.
      2.  Immediately after, call the `check_claim_history` function (from Step 3.3) with the _same_ sample claim text.
      3.  Verify that `check_claim_history` now returns the data that was just upserted, matching the provided verdict and explanation.
      4.  Optionally, use `claims_collection.count()` to verify the number of items in the collection has increased.
      5.  Test error scenarios and verify proper logging.

5.  **Step 3.5: Integrate Claim History into Analysis Workflow**
    - **Instruction:** Modify the `/analyze_claim` POST endpoint:
      1.  At the beginning of the endpoint, call `check_claim_history` with the incoming `request.claim_text`.
      2.  If a historical entry is found, return a JSON response containing the `received_claim`, stored `verdict`, `explanation`, a `source` field indicating "claim_history", and the stored `timestamp`. Do not proceed to web search or LLM processing.
      3.  If no historical entry is found, proceed with web search and LLM processing as before.
      4.  After obtaining a new verdict and explanation from the LLM (and if the analysis was successful, e.g., no errors), call `update_claim_history` to save this new analysis to the database. Ensure the `source` field in the response indicates "new_analysis".
      5.  Add comprehensive error handling and logging throughout.
    - **Test:**
      1.  Send a POST request to `/analyze_claim` with a _new_ news claim. Verify the response indicates `source: "new_analysis"` and the backend logs show calls to web search, LLM, and database update.
      2.  Send _another_ POST request to `/analyze_claim` with the _exact same_ news claim. Verify the response now indicates `source: "claim_history"`, contains the previously determined verdict/explanation, and backend logs show that web search and LLM processing were skipped.

---

## Phase 4: Basic Frontend Integration

**Objective:** Connect the basic frontend to the backend API to submit claims and display results with loading states.

1.  **Step 4.1: Frontend JavaScript to Call Backend API**

    - **Instruction:** In `frontend/script.js`:
      1.  Add an event listener to the "Analyze Claim" button.
      2.  When the button is clicked, show the loading indicator and disable the button to prevent multiple submissions.
      3.  Retrieve the text from the `claimInput` textarea.
      4.  Use the `fetch` API to send an asynchronous POST request to the backend's `/analyze_claim` endpoint (`http://127.0.0.1:8000/analyze_claim`). The request body must be JSON containing the claim text (e.g., `{"claim_text": "user's input"}`). Set the `Content-Type` header to `application/json`.
      5.  Configure CORS middleware in the backend FastAPI application to allow requests from the frontend's origin for development.
      6.  Hide the loading indicator and re-enable the button when the request completes (success or error).
    - **Test:**
      1.  Open `frontend/index.html` in a browser. Ensure the backend FastAPI server is running.
      2.  Enter a sample claim into the textarea and click the "Analyze Claim" button.
      3.  Verify that the loading indicator appears and the button is disabled during the request.
      4.  Open the browser's developer console (Network tab). Verify that a POST request is made to `http://127.0.0.1:8000/analyze_claim` with the correct JSON payload.
      5.  Verify the request receives a 200 OK response from the server and the loading state is properly managed.

2.  **Step 4.2: Display Backend Response on Frontend**
    - **Instruction:** In `frontend/script.js`, within the `fetch` call's success handler (e.g., `.then(response => response.json()).then(data => ...)`):
      1.  Parse the JSON response received from the backend.
      2.  Update the `textContent` of the HTML elements designated for displaying the verdict (e.g., `verdictText`) and explanation (e.g., `explanationText`) with the corresponding values (`data.verdict` and `data.explanation`) from the parsed JSON response. Handle cases where verdict or explanation might be missing.
      3.  Add error handling for failed requests and display appropriate error messages to the user.
    - **Test:**
      1.  Enter a sample claim in the `frontend/index.html` page and click "Analyze Claim".
      2.  Verify that the loading indicator works correctly during the request.
      3.  Verify that the "Verdict:" and "Explanation:" sections on the webpage are updated with the actual verdict and explanation returned by the backend API. The displayed text should change from its initial placeholder state.
      4.  Test error scenarios and verify appropriate error messages are displayed.

---

## Phase 5: Basic Feedback Loop (Stub)

**Objective:** Implement UI elements for feedback and a backend endpoint to log this feedback (no model retraining in MVP, just data logging).

1.  **Step 5.1: Add Feedback UI Elements on Frontend**

    - **Instruction:**
      1.  In `frontend/index.html`, add a new `div` (e.g., with ID `feedbackSection`) below the results display area. Inside this div, add two buttons (e.g., "✔️ Accurate", "❌ Inaccurate") and a paragraph element for displaying feedback submission messages (e.g., ID `feedbackMessage`).
      2.  Initially, set this `feedbackSection` to be hidden using CSS (`display: none`).
      3.  In `frontend/script.js`, after successfully displaying the analysis results (from Step 4.2), change the `display` style of the `feedbackSection` to `block` (or `flex`, etc.) to make it visible. Clear any previous message in `feedbackMessage`.
    - **Test:**
      - Process a claim through the UI by entering text and clicking "Analyze Claim".
      - Verify that after the verdict and explanation are displayed, the "Accurate" and "Inaccurate" buttons and the feedback message area become visible on the page.

2.  **Step 5.2: Create Backend Endpoint for Receiving Feedback**

    - **Instruction:**
      1.  In `backend/main.py`, define a Pydantic model for the feedback request, expecting `claim_text` (the original claim being rated) and `feedback_type` (e.g., "accurate" or "inaccurate").
      2.  Create a new POST endpoint at `/submit_feedback` that accepts a JSON payload matching this Pydantic model.
      3.  Upon receiving feedback, this endpoint should:
          a. Log the received `claim_text` and `feedback_type` to the server console.
          b. (Database Update) Generate the claim ID from `claim_text` (as in Step 3.3). Attempt to retrieve the existing entry from ChromaDB. If found, update its metadata to include the new `user_feedback` (e.g., "accurate") and a `feedback_timestamp`. Use `claims_collection.update()` for this.
          c. Return a JSON response indicating success or failure of the feedback submission (e.g., `{"message": "Feedback submitted and logged."}`).
          d. Add comprehensive error handling and logging for feedback operations.
    - **Test:**
      1.  First, analyze a claim through the UI so it exists in ChromaDB. Note the exact claim text.
      2.  Use `curl` or Postman to send a POST request to `http://127.0.0.1:8000/submit_feedback` with a JSON payload like `{"claim_text": "the exact claim text analyzed earlier", "feedback_type": "accurate"}`.
      3.  Check the backend server's console logs. Verify that the feedback details (claim text and type) are printed.
      4.  Verify the API response indicates success.
      5.  (Database Verification) Query ChromaDB for the claim ID. Check its metadata to confirm `user_feedback` and `feedback_timestamp` fields were added/updated.

3.  **Step 5.3: Frontend JavaScript to Send Feedback to Backend**

    - **Instruction:**
      1.  In `frontend/script.js`, store the current `claim_text` in a variable when the "Analyze Claim" button is clicked and analysis is initiated.
      2.  Add event listeners to the "Accurate" and "Inaccurate" feedback buttons.
      3.  When a feedback button is clicked, use the `fetch` API to send an asynchronous POST request to the backend's `/submit_feedback` endpoint. The request body should be JSON containing the stored `currentClaimForFeedback` and the respective `feedback_type` ("accurate" or "inaccurate").
      4.  Display the message from the backend's response in the `feedbackMessage` paragraph on the UI.
      5.  Add error handling for failed feedback submissions.
    - **Test:**
      1.  Process a claim through the UI.
      2.  After results are displayed, click either the "Accurate" or "Inaccurate" button.
      3.  Check the browser's Network tab to verify a POST request is sent to `/submit_feedback` with the correct claim text and feedback type.
      4.  Check the backend server logs to confirm the feedback was received.
      5.  Verify that the `feedbackMessage` paragraph on the UI is updated with the confirmation message from the backend.

4.  **Step 5.4: Verify Feedback Persistence in Database via UI Workflow**

    - **Instruction:** This step re-validates the end-to-end feedback logging into the database, initiated from the UI.
    - **Test:**
      1.  Analyze a completely new claim using the `frontend/index.html` UI to ensure it's processed and stored in ChromaDB.
      2.  Click one of the feedback buttons (e.g., "Accurate") for this newly analyzed claim.
      3.  Verify the UI shows a success message for feedback submission.
      4.  On the backend, confirm (via logs or by programmatically querying/inspecting the ChromaDB entry for that specific claim ID) that the metadata for the claim now includes the `user_feedback` (e.g., "accurate") and a `feedback_timestamp`.

5.  **Step 5.5: Final Documentation Update**
    - **Instruction:** Update `memory-bank/architecture.md` with the complete system architecture. Update `memory-bank/progress.md` to reflect MVP completion. Document any important findings or decisions made during implementation.
    - **Test:**
      - Verify that both files accurately reflect the completed MVP system.

---

## Integration Testing

**Objective:** Ensure the complete workflow functions correctly end-to-end.

1.  **Step IT.1: Complete Workflow Test**
    - **Test:**
      1.  Start the backend server and open the frontend in a browser.
      2.  Submit a completely new claim and verify the full pipeline: loading state → web search → LLM analysis → database storage → result display → feedback collection.
      3.  Submit the same claim again and verify it's retrieved from claim history.
      4.  Test error scenarios: invalid input, network failures, API failures.
      5.  Verify all operations are properly logged.

This MVP implementation plan provides a foundational, end-to-end working system focused on web search-based fact checking. The database integration is temporary for MVP purposes, with full database implementation planned for later iterations.
