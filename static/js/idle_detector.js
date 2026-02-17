// ===============================
// DASHBOARD ACTIVE CHECK
// ===============================
function isDashboardActive() {
    const dashboard = document.getElementById("dashboard");
    return dashboard && dashboard.classList.contains("active");
}


// ===============================
// STATE VARIABLES
// ===============================
let lastActivity = Date.now();
let idlePaused = false;
let checkingGame = false;


// ===============================
// TRACK USER ACTIVITY
// ===============================
["mousemove", "keydown", "click", "scroll"].forEach(evt => {
    document.addEventListener(evt, () => {
        if (isDashboardActive()) {
            lastActivity = Date.now();
        }
    });
});


// ===============================
// IDLE DETECTION (Runs every 5s)
// ===============================
setInterval(() => {

    // Run ONLY if dashboard is visible
    if (!isDashboardActive()) return;

    if (idlePaused) return;

    const idleTime = Date.now() - lastActivity;

    if (idleTime > 10000) {   // 10 seconds idle
        console.log("🧠 Idle detected");

        fetch("/report_idle", { method: "POST" })
            .catch(err => console.log("Idle report failed:", err));

        lastActivity = Date.now();
    }

}, 5000);



// ===============================
// POLL FOR PENDING GAME (every 3s)
// ===============================
setInterval(() => {

    // Only when dashboard active
    if (!isDashboardActive()) return;

    if (idlePaused || checkingGame) return;

    checkingGame = true;

    fetch("/pending_game")
        .then(res => res.json())
        .then(data => {
            if (data.ok && data.url) {
                showPopupThenGame(data.url);
            }
        })
        .catch(err => console.error("Pending game error:", err))
        .finally(() => {
            checkingGame = false;
        });

}, 3000);



// ===============================
// POPUP → GAME FLOW
// ===============================
function showPopupThenGame(gameUrl) {

    const popup = document.getElementById("popup");
    const overlay = document.getElementById("game-overlay");
    const iframe = document.getElementById("game-iframe");

    idlePaused = true;

    if (popup) popup.style.display = "flex";

    setTimeout(() => {

        if (popup) popup.style.display = "none";

        if (iframe) iframe.src = gameUrl;
        if (overlay) overlay.style.display = "flex";

    }, 3000);
}



// ===============================
// CLOSE GAME
// ===============================
function closeGame() {

    const overlay = document.getElementById("game-overlay");
    const iframe = document.getElementById("game-iframe");

    if (overlay) overlay.style.display = "none";
    if (iframe) iframe.src = "";

    idlePaused = false;
    lastActivity = Date.now();

    fetch("/log_game_result", { method: "POST" })
        .catch(err => console.log("Log result failed:", err));
}



// ===============================
// LISTEN FOR GAME FINISH (iframe)
// ===============================
window.addEventListener("message", function(event) {

    if (!event.data) return;

    if (event.data.type === "game_finished") {
        console.log("Game finished received from iframe");
        closeGame();
    }

});
