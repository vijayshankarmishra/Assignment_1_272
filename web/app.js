const WORD_BANK = [
  "python", "developer", "keyboard", "notebook", "algorithm", "function", "variable",
  "compose", "docker", "github", "machine", "learning", "network", "browser",
  "package", "library", "module", "integer", "string", "boolean", "operator",
  "system", "process", "thread", "memory", "storage", "buffer", "socket", "server",
  "client", "request", "response", "timeout", "session", "cookie", "token",
];

function maskWord(word) {
  if (word.length <= 2) return "_".repeat(word.length);
  const count = Math.floor(Math.random() * Math.max(1, word.length - 1)) + 1; // 1..len-1
  const idxs = [...Array(word.length).keys()].sort(() => 0.5 - Math.random()).slice(0, count);
  const hidden = new Set(idxs);
  return word.split("").map((ch, i) => hidden.has(i) ? "_" : ch).join("");
}

function generateOptions(answer, bank, k = 4) {
  const sameLen = bank.filter(w => w !== answer && w.length === answer.length);
  const pool = sameLen.length >= k - 1 ? sameLen : bank.filter(w => w !== answer);
  const shuffled = pool.sort(() => 0.5 - Math.random());
  const distractors = shuffled.slice(0, Math.min(k - 1, shuffled.length));
  const options = [...distractors, answer].sort(() => 0.5 - Math.random());
  const correctIndex = options.indexOf(answer);
  return { options, correctIndex };
}

const state = {
  score: 0,
  round: 0,
  totalRounds: 10,
  current: null,
};

function nextQuestion() {
  state.round += 1;
  const answer = WORD_BANK[Math.floor(Math.random() * WORD_BANK.length)];
  const masked = maskWord(answer);
  const { options, correctIndex } = generateOptions(answer, WORD_BANK, 4);
  state.current = { answer, masked, options, correctIndex };
  render();
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
    btn.onclick = () => select(i, btn);
    optionsEl.appendChild(btn);
  });
}

function select(index, btn) {
  const correct = index === state.current.correctIndex;
  if (correct) {
    state.score += 1;
    btn.classList.add("correct");
  } else {
    btn.classList.add("wrong");
    // highlight the correct one
    const buttons = Array.from(document.querySelectorAll(".option"));
    buttons[state.current.correctIndex].classList.add("correct");
  }
  // disable all
  document.querySelectorAll(".option").forEach(b => b.disabled = true);
}

window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("nextBtn").addEventListener("click", () => {
    if (state.round >= state.totalRounds) {
      state.score = 0; state.round = 0; // restart
    }
    nextQuestion();
  });
  nextQuestion();
});
