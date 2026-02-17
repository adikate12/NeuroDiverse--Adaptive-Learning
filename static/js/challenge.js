const colors = ["red", "blue", "green", "yellow", "purple", "orange"];
const words = ["RED", "BLUE", "GREEN", "YELLOW", "PURPLE", "ORANGE"];

let score = 0;
let total = 0;
let timeLeft = 30;
let active = true;

const wordEl = document.getElementById("word");
const btnContainer = document.getElementById("buttons");
const timerEl = document.getElementById("timer");
const returnBtn = document.getElementById("returnBtn");

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function newRound() {
  if (!active) return;

  const text = randomChoice(words);
  const color = randomChoice(colors);

  wordEl.textContent = text;
  wordEl.style.color = color;
}

function renderButtons() {
  btnContainer.innerHTML = "";

  colors.forEach((c) => {
    const btn = document.createElement("button");
    btn.className = "color-btn";
    btn.style.background = c;
    btn.textContent = c.toUpperCase();
    btn.onclick = () => checkAnswer(c);
    btnContainer.appendChild(btn);
  });
}

function checkAnswer(selected) {
  if (!active) return;

  const correct = wordEl.style.color;

  total++;
  if (selected === correct) {
    score++;
  }

  newRound();
}

function startTimer() {
  const interval = setInterval(() => {
    timeLeft--;
    timerEl.textContent = `Time Left: ${timeLeft} s`;

    if (timeLeft <= 0) {
      clearInterval(interval);
      endGame();
    }
  }, 1000);

  // Notify parent that game started (pause idle detection)
  if (window.parent && window.parent.postMessage) {
    window.parent.postMessage({ type: "game_started" }, "*");
  }
}

function endGame() {
  active = false;

  wordEl.textContent = `Final Score: ${score}/${total}`;
  btnContainer.innerHTML = "";
  timerEl.textContent = "Great job! 🧠";
  returnBtn.style.display = "inline-block";

  // ✅ Correct game name
  fetch("/log_game_result", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ game: "challenge", score: score }),
  });

  returnBtn.onclick = () => {
    if (window.parent && window.parent.postMessage) {
      window.parent.postMessage(
        { type: "game_finished", game: "challenge" },
        "*"
      );
    }
  };
}

// Initialize game
renderButtons();
newRound();
startTimer();
