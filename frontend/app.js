// API Configuration
const API_BASE_URL = '/api';

const state = {
  score: 0,
  round: 0,
  totalRounds: 10,
  current: null,
  sessionId: generateSessionId(),
};

function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Fetch new question from backend
async function fetchQuestion() {
  try {
    const response = await fetch(`${API_BASE_URL}/quiz/question`);
    if (!response.ok) throw new Error('Failed to fetch question');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching question:', error);
    showFeedback('Error loading question. Please try again.', 'error');
    return null;
  }
}

// Submit answer to backend
async function submitAnswer(selectedOption, isCorrect) {
  try {
    const payload = {
      sessionId: state.sessionId,
      question: state.current.masked,
      answer: state.current.answer,
      selectedOption: selectedOption,
      correct: isCorrect,
      round: state.round,
      timestamp: new Date().toISOString(),
    };
    
    const response = await fetch(`${API_BASE_URL}/quiz/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) throw new Error('Failed to submit answer');
    return await response.json();
  } catch (error) {
    console.error('Error submitting answer:', error);
  }
}

// Fetch statistics from metrics service
async function fetchStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/metrics/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return await response.json();
  } catch (error) {
    console.error('Error fetching stats:', error);
    return null;
  }
}

async function nextQuestion() {
  if (state.round >= state.totalRounds) {
    await showFinalScore();
    return;
  }

  state.round += 1;
  showFeedback('Loading question...', 'info');
  
  const question = await fetchQuestion();
  if (!question) {
    showFeedback('Failed to load question', 'error');
    return;
  }

  state.current = question;
  render();
  clearFeedback();
}

function render() {
  const maskedEl = document.getElementById("masked");
  const optionsEl = document.getElementById("options");
  const scoreEl = document.getElementById("score");
  const roundEl = document.getElementById("round");

  maskedEl.textContent = state.current.masked;
  scoreEl.textContent = `Score: ${state.score}`;
  roundEl.textContent = `Round: ${state.round}/${state.totalRounds}`;

  optionsEl.innerHTML = "";
  state.current.options.forEach((opt, i) => {
    const btn = document.createElement("button");
    btn.className = "option";
    btn.textContent = opt;
    btn.onclick = () => select(opt, i, btn);
    optionsEl.appendChild(btn);
  });
}

async function select(selectedOption, index, btn) {
  const correct = index === state.current.correctIndex;
  
  if (correct) {
    state.score += 1;
    btn.classList.add("correct");
    showFeedback("✅ Correct! +1 point", "success");
  } else {
    btn.classList.add("wrong");
    const buttons = Array.from(document.querySelectorAll(".option"));
    buttons[state.current.correctIndex].classList.add("correct");
    showFeedback(`❌ Wrong. The correct answer was "${state.current.answer}"`, "error");
  }
  
  // Update score display immediately
  document.getElementById("score").textContent = `Score: ${state.score}`;
  
  // Disable all buttons
  document.querySelectorAll(".option").forEach(b => b.disabled = true);
  
  // Submit answer to backend
  await submitAnswer(selectedOption, correct);
}

function showFeedback(message, type) {
  const feedbackEl = document.getElementById("feedback");
  feedbackEl.textContent = message;
  feedbackEl.className = `feedback ${type}`;
  feedbackEl.style.display = 'block';
}

function clearFeedback() {
  const feedbackEl = document.getElementById("feedback");
  feedbackEl.style.display = 'none';
}

async function showFinalScore() {
  const feedbackEl = document.getElementById("feedback");
  feedbackEl.innerHTML = `
    <h2>🎉 Quiz Complete!</h2>
    <p>Your final score: <strong>${state.score}/${state.totalRounds}</strong></p>
    <p>Percentage: <strong>${((state.score / state.totalRounds) * 100).toFixed(1)}%</strong></p>
    <button onclick="restartQuiz()">Play Again</button>
  `;
  feedbackEl.className = 'feedback success';
  feedbackEl.style.display = 'block';
}

function restartQuiz() {
  state.score = 0;
  state.round = 0;
  state.sessionId = generateSessionId();
  clearFeedback();
  nextQuestion();
}

async function showStats() {
  const statsPanel = document.getElementById("stats");
  const statsContent = document.getElementById("statsContent");
  
  statsPanel.style.display = 'block';
  statsContent.innerHTML = '<p>Loading statistics...</p>';
  
  const stats = await fetchStats();
  if (stats) {
    statsContent.innerHTML = `
      <div class="stat-item">
        <span class="stat-label">Total Questions Answered:</span>
        <span class="stat-value">${stats.totalQuestions || 0}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Correct Answers:</span>
        <span class="stat-value">${stats.correctAnswers || 0}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Overall Accuracy:</span>
        <span class="stat-value">${stats.accuracy || '0.0'}%</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Total Sessions:</span>
        <span class="stat-value">${stats.totalSessions || 0}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Average Score:</span>
        <span class="stat-value">${stats.averageScore || '0.0'}/10</span>
      </div>
    `;
  } else {
    statsContent.innerHTML = '<p>Failed to load statistics.</p>';
  }
}

function hideStats() {
  const statsPanel = document.getElementById("stats");
  statsPanel.style.display = 'none';
}

// Initialize app
window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("nextBtn").addEventListener("click", nextQuestion);
  document.getElementById("statsBtn").addEventListener("click", showStats);
  document.getElementById("closeStatsBtn").addEventListener("click", hideStats);
  
  // Load first question
  nextQuestion();
});
