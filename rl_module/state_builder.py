def compute_learning_state(attention, games, ml_profile):
    """
    attention: {"focused": x, "distracted": y}
    games: {
        "game1": [ {score:..}, ... ],
        "game2": [ ... ],
        "relax": [ ... ],
        "challenge": [ ... ]
    }
    ml_profile: PI / PH / C
    """

    # -----------------------------
    # 1️⃣ Focus ratio (safe)
    # -----------------------------
    focused = attention.get("focused", 0)
    distracted = attention.get("distracted", 0)

    total = focused + distracted
    focus_ratio = focused / total if total > 0 else 0.5

    # -----------------------------
    # 2️⃣ Collect recent games
    # -----------------------------
    all_games = []
    if isinstance(games, dict):
        for game_list in games.values():
            if isinstance(game_list, list):
                all_games.extend(game_list)

    recent = all_games[-3:] if len(all_games) >= 3 else all_games

    # -----------------------------
    # 3️⃣ Score bonus
    # -----------------------------
    score_bonus = 0
    if recent:
        avg_score = sum(g.get("score", 0) for g in recent) / len(recent)
        score_bonus = avg_score / 100.0  # normalize to 0–1

    # -----------------------------
    # 4️⃣ ADHD profile penalty
    # -----------------------------
    profile_penalty = 0
    if ml_profile == "PI":
        profile_penalty = -1
    elif ml_profile == "PH":
        profile_penalty = -0.5

    # -----------------------------
    # 5️⃣ Final discrete state (0–10)
    # -----------------------------
    state = int((focus_ratio * 6) + (score_bonus * 3) + profile_penalty)

    return max(0, min(10, state))
