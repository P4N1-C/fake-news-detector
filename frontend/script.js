/**
 * AI-Powered Fake News Detector - Frontend JavaScript
 * Handles user interactions and API communication
 */

// DOM elements
const claimInput = document.getElementById("claimInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const loadingIndicator = document.getElementById("loadingIndicator");
const resultsSection = document.getElementById("resultsSection");
const verdictText = document.getElementById("verdictText");
const explanationText = document.getElementById("explanationText");
const serpApiResultsList = document.getElementById("serpApiResultsList");
const duckDuckGoResultsList = document.getElementById("duckDuckGoResultsList");
const tavilyResultsList = document.getElementById("tavilyResultsList");
const serpApiResultsContainer = document.getElementById(
  "serpApiResultsContainer"
);
const duckDuckGoResultsContainer = document.getElementById(
  "duckDuckGoResultsContainer"
);
const tavilyResultsContainer = document.getElementById(
  "tavilyResultsContainer"
);
const noResultsContainer = document.getElementById("noResultsContainer");

// Feedback elements
const feedbackSection = document.getElementById("feedbackSection");
const accurateBtn = document.getElementById("accurateBtn");
const inaccurateBtn = document.getElementById("inaccurateBtn");
const feedbackMessage = document.getElementById("feedbackMessage");

// API configuration
const API_BASE_URL = "http://127.0.0.1:8000";

// Global variable to store current claim for feedback
let currentClaimForFeedback = "";

/**
 * Initialize the application
 */
document.addEventListener("DOMContentLoaded", function () {
  // Add event listeners
  analyzeBtn.addEventListener("click", handleAnalyzeClaim);

  // Add feedback event listeners
  accurateBtn.addEventListener("click", () => handleFeedback("accurate"));
  inaccurateBtn.addEventListener("click", () => handleFeedback("inaccurate"));

  // Allow Enter key to trigger analysis
  claimInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter" && e.ctrlKey) {
      handleAnalyzeClaim();
    }
  });

  console.log("Fake News Detector frontend initialized");
});

/**
 * Handle the analyze claim button click
 */
async function handleAnalyzeClaim() {
  const claimText = claimInput.value.trim();

  // Validate input
  if (!claimText) {
    alert("Please enter a news claim to analyze.");
    claimInput.focus();
    return;
  }

  // Store claim text for feedback
  currentClaimForFeedback = claimText;

  // Show loading state
  setLoadingState(true);
  hideResults();
  hideFeedback();

  try {
    console.log("Analyzing claim:", claimText);

    // Call the backend API
    const response = await fetch(`${API_BASE_URL}/analyze_claim`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        claim_text: claimText,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Received analysis results:", data);

    // Display the results
    displayResults(data);
    setLoadingState(false);

    // Show feedback section after successful analysis
    showFeedback();
  } catch (error) {
    console.error("Error analyzing claim:", error);
    showError(
      "An error occurred while analyzing the claim. Please check if the backend server is running and try again."
    );
    setLoadingState(false);
  }
}

/**
 * Handle feedback submission
 */
async function handleFeedback(feedbackType) {
  if (!currentClaimForFeedback) {
    console.error("No claim available for feedback");
    feedbackMessage.textContent = "Error: No claim available for feedback.";
    feedbackMessage.className = "feedback-message feedback-error";
    return;
  }

  // Disable feedback buttons during submission
  accurateBtn.disabled = true;
  inaccurateBtn.disabled = true;
  feedbackMessage.textContent = "Submitting feedback...";
  feedbackMessage.className = "feedback-message feedback-pending";

  try {
    console.log(
      `Submitting ${feedbackType} feedback for claim:`,
      currentClaimForFeedback
    );

    // Call the backend feedback API
    const response = await fetch(`${API_BASE_URL}/submit_feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        claim_text: currentClaimForFeedback,
        feedback_type: feedbackType,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Feedback response:", data);

    // Display success message
    feedbackMessage.textContent =
      data.message || "Feedback submitted successfully!";
    feedbackMessage.className = "feedback-message feedback-success";

    // Keep buttons disabled after successful submission
    console.log(`Successfully submitted ${feedbackType} feedback`);
  } catch (error) {
    console.error("Error submitting feedback:", error);
    feedbackMessage.textContent =
      "Failed to submit feedback. Please try again.";
    feedbackMessage.className = "feedback-message feedback-error";

    // Re-enable buttons on error
    accurateBtn.disabled = false;
    inaccurateBtn.disabled = false;
  }
}

/**
 * Display the analysis results
 */
function displayResults(data) {
  // Display verdict with appropriate styling
  verdictText.textContent = data.verdict || "Unknown";
  verdictText.className = `verdict-text ${getVerdictClass(data.verdict)}`;

  // Display explanation
  explanationText.textContent = data.explanation || "No explanation provided.";

  // Display search results
  displaySearchResults(data.search_results || []);

  // Show results section
  showResults();
}

/**
 * Get CSS class for verdict styling
 */
function getVerdictClass(verdict) {
  if (!verdict) return "";

  const verdictLower = verdict.toLowerCase();
  if (verdictLower.includes("true")) return "verdict-true";
  if (verdictLower.includes("false")) return "verdict-false";
  if (verdictLower.includes("uncertain") || verdictLower.includes("needs more"))
    return "verdict-uncertain";
  if (verdictLower.includes("error")) return "verdict-error";
  return "";
}

/**
 * Display search results separated by source
 */
function displaySearchResults(searchResults) {
  // Clear previous results
  serpApiResultsList.innerHTML = "";
  duckDuckGoResultsList.innerHTML = "";
  tavilyResultsList.innerHTML = "";

  // Hide all containers initially
  serpApiResultsContainer.style.display = "none";
  duckDuckGoResultsContainer.style.display = "none";
  tavilyResultsContainer.style.display = "none";
  noResultsContainer.style.display = "none";

  if (!searchResults || searchResults.length === 0) {
    noResultsContainer.style.display = "block";
    return;
  }

  console.log("All search results:", searchResults);

  // Separate results by source
  const serpApiResults = searchResults.filter(
    (result) => result.source === "SerpAPI"
  );
  const duckDuckGoResults = searchResults.filter(
    (result) => result.source === "DuckDuckGo"
  );
  const tavilyResults = searchResults.filter(
    (result) => result.source === "Tavily"
  );

  console.log("Tavily results:", tavilyResults);

  // Display SerpAPI results
  if (serpApiResults.length > 0) {
    serpApiResultsContainer.style.display = "block";
    displayResultsInContainer(serpApiResults, serpApiResultsList);
  }

  // Display DuckDuckGo results
  if (duckDuckGoResults.length > 0) {
    duckDuckGoResultsContainer.style.display = "block";
    displayResultsInContainer(duckDuckGoResults, duckDuckGoResultsList);
  }

  // Display Tavily results
  if (tavilyResults.length > 0) {
    console.log("Displaying Tavily results container");
    tavilyResultsContainer.style.display = "block";
    displayResultsInContainer(tavilyResults, tavilyResultsList);
  } else {
    console.log("No Tavily results to display");
  }
}

/**
 * Display results in a specific container
 */
function displayResultsInContainer(results, container) {
  results.forEach((result, index) => {
    const resultDiv = document.createElement("div");
    resultDiv.className = "search-result-item";

    resultDiv.innerHTML = `
      <div class="search-result-header">
        <span class="search-result-number">${index + 1}.</span>
        <h4 class="search-result-title">${escapeHtml(
          result.title || "No title"
        )}</h4>
      </div>
      <p class="search-result-snippet">${escapeHtml(
        result.snippet || "No content available"
      )}</p>
    `;

    container.appendChild(resultDiv);
  });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Set loading state
 */
function setLoadingState(isLoading) {
  if (isLoading) {
    loadingIndicator.style.display = "block";
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "🔄 Analyzing...";
  } else {
    loadingIndicator.style.display = "none";
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "🔍 Analyze Claim";
  }
}

/**
 * Show results section
 */
function showResults() {
  resultsSection.style.display = "block";
}

/**
 * Hide results section
 */
function hideResults() {
  resultsSection.style.display = "none";
}

/**
 * Show feedback section
 */
function showFeedback() {
  feedbackSection.style.display = "block";
  // Clear any previous feedback message
  feedbackMessage.textContent = "";
  feedbackMessage.className = "feedback-message";
  // Re-enable feedback buttons
  accurateBtn.disabled = false;
  inaccurateBtn.disabled = false;
}

/**
 * Hide feedback section
 */
function hideFeedback() {
  feedbackSection.style.display = "none";
}

/**
 * Show error message
 */
function showError(message) {
  verdictText.textContent = "Error";
  verdictText.className = "verdict-text verdict-error";
  explanationText.textContent = message;

  // Clear search results
  serpApiResultsList.innerHTML = "";
  duckDuckGoResultsList.innerHTML = "";
  tavilyResultsList.innerHTML = "";
  serpApiResultsContainer.style.display = "none";
  duckDuckGoResultsContainer.style.display = "none";
  tavilyResultsContainer.style.display = "none";
  noResultsContainer.style.display = "block";

  showResults();
}
