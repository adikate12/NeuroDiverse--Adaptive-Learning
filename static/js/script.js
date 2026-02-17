// ========================================
// INITIALIZATION AND LOADING
// ========================================

// Loading Screen
window.addEventListener('load', function() {
    setTimeout(function() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
        }
    }, 2500);
});


// ========================================
// USER PROFILE HANDLING
// ========================================

(function initializeProfile() {
    const dataEl = document.getElementById('profileData');
    if (!dataEl) return;

    const code = dataEl.dataset.code;
    const label = dataEl.dataset.label;
    const att = dataEl.dataset.att;
    const imp = dataEl.dataset.imp;
    const org = dataEl.dataset.org;
    const wm = dataEl.dataset.wm;

    const fab = document.getElementById('profileFab');
    const card = document.getElementById('profileCard');
    const tag = document.getElementById('profileTag');
    const title = document.getElementById('profileTitle');
    const message = document.getElementById('profileMessage');
    const scores = document.getElementById('profileScores');

    if (!fab || !card) return;

    let friendlyMsg = "";

    if (code === 'PI') {
        friendlyMsg = "Hi! Staying focused can be tricky sometimes. We'll help you with short focus games and simple study steps. 💫";
    } else if (code === 'PH') {
        friendlyMsg = "Hi! You've got lots of energy. We'll help you channel it in a smart way. ⚡";
    } else if (code === 'C') {
        friendlyMsg = "Hi! We'll balance focus boosts and calming tools step by step. 🌈";
    } else {
        friendlyMsg = "Hi! We're learning about your style. We'll guide you gently. 🌱";
    }

    tag.textContent = label || "Profile";
    title.textContent = "Your learning profile";
    message.textContent = friendlyMsg;
    scores.textContent =
        `Attention: ${att}/100 · Impulse: ${imp}/100 · Organization: ${org}/100 · Memory: ${wm}/100`;

    let visible = false;
    fab.addEventListener('click', () => {
        visible = !visible;
        card.style.display = visible ? 'block' : 'none';
    });
})();


// ========================================
// NAVIGATION
// ========================================

function showPage(pageName, el) {

    const pages = document.querySelectorAll('.page-container');
    pages.forEach(page => page.classList.remove('active'));

    const selectedPage = document.getElementById(pageName);
    if (selectedPage) {
        selectedPage.classList.add('active');
    }

    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => link.classList.remove('active'));

    if (el) el.classList.add('active');

    const navMenu = document.getElementById('navMenu');
    if (navMenu) navMenu.classList.remove('active');
}


// Mobile Menu Toggle
function toggleMobileMenu() {
    const navMenu = document.getElementById('navMenu');
    if (navMenu) navMenu.classList.toggle('active');
}


// Focus Break (placeholder)
function showFocusBreak() {
    alert('🧘 Focus Break coming soon! Take a breath and stretch.');
}


// ========================================
// DISTRACTION STATUS CHECK
// ========================================

function showPopup() {
    const popup = document.getElementById("popup");
    if (popup) {
        popup.style.display = "flex";
        setTimeout(() => popup.style.display = "none", 4000);
    }
}

async function checkDistraction() {
    try {
        const response = await fetch('/check_distraction');
        const data = await response.json();

        const alertBox = document.getElementById("alertBox");
        const statusBadge = document.getElementById("statusBadge");

        if (!alertBox || !statusBadge) return;

        if (data.distracted) {
            alertBox.textContent = "Distracted ⚠️";
            alertBox.classList.add("distracted");
            statusBadge.style.background = "#ef4444";
            showPopup();
        } else {
            alertBox.textContent = "Focused ✅";
            alertBox.classList.remove("distracted");
            statusBadge.style.background = "#10b981";
        }

    } catch (error) {
        console.error("Error checking distraction:", error);
    }
}

setInterval(checkDistraction, 2000);


// ========================================
// MANUAL GAME TRIGGER (DEBUG)
// ========================================

window.triggerAttentionGame = async function(type) {
    try {
        await fetch('/trigger_game', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ type: type })
        });
    } catch (err) {
        console.error("Failed to trigger game:", err);
    }
};


// ========================================
// IDLE MONITOR (Lightweight only)
// ========================================

let idleTime = 0;

function resetIdleTime() {
    idleTime = 0;
}

document.addEventListener('mousemove', resetIdleTime);
document.addEventListener('keypress', resetIdleTime);
document.addEventListener('click', resetIdleTime);
document.addEventListener('scroll', resetIdleTime);

setInterval(() => {
    idleTime++;
}, 1000);


// ========================================
// STUDY TIME TRACKING
// ========================================

let studyStartTime = Date.now();

function updateStudyTime() {
    const elapsed = Math.floor((Date.now() - studyStartTime) / 1000 / 60);
    const studyTimeEl = document.getElementById('studyTime');
    if (studyTimeEl) {
        studyTimeEl.textContent = elapsed + ' min';
    }
}

setInterval(updateStudyTime, 10000);


// ========================================
// BUTTON EFFECTS
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn, .social-icon');
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => this.style.transform = '', 100);
        });
    });
});


// ========================================
// CONSOLE MESSAGE
// ========================================

console.log('%c🧠 NeuroDiverse Learning Platform', 
    'font-size: 20px; color: #667eea; font-weight: bold;');
console.log('%cAdaptive learning for every mind!', 
    'font-size: 14px; color: #718096;');
