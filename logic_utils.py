import random


# FIX: Extracted the New Game reset out of app.py's Streamlit block into this
# pure function with Claude (agent mode) so it could be unit-tested. The rng
# is injectable to make the range check deterministic in tests.
def new_game_state(low, high, rng=None):
    """Build the session-state fields for a fresh game.

    Centralizes the "New Game" reset. The original bug only reset `attempts`
    and `secret`, leaving `status` (won/lost) and `history` stale, and it
    hardcoded a 1-100 range instead of honoring the difficulty's (low, high).
    """
    if rng is None:
        rng = random.randint
    return {
        "attempts": 0,
        "secret": rng(low, high),
        "status": "playing",
        "history": [],
    }


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX: Refactored check_guess from app.py into logic_utils.py with Claude (agent mode),
    # and swapped the inverted hints — too-high now says "Go LOWER", too-low says "Go HIGHER".
    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


# FEATURE (Challenge 2): Guess History sidebar. Built agentically with Claude.
# Pure function so the closeness math is unit-tested in tests/test_game_logic.py
# and the app.py sidebar only handles rendering.
def guess_proximity(guess, secret, low, high):
    """Describe how close a guess is to the secret.

    Returns (label, closeness, direction):
      - label: a hot/cold string for how near the guess was
      - closeness: float in [0.0, 1.0], where 1.0 means exact
      - direction: "up" if the secret is higher than the guess, "down" if lower,
        "hit" if exact (i.e. which way the player should move next)

    closeness is normalized against the active (low, high) range so the same
    distance feels equally "warm" on Easy (1-20) and Normal (1-100).
    """
    span = max(1, high - low)
    distance = abs(guess - secret)
    closeness = max(0.0, 1.0 - distance / span)

    if distance == 0:
        return "🎯 Exact!", 1.0, "hit"
    if closeness >= 0.85:
        label = "🔥 Burning hot"
    elif closeness >= 0.6:
        label = "🌡️ Warm"
    elif closeness >= 0.35:
        label = "😎 Cool"
    else:
        label = "❄️ Cold"

    direction = "up" if secret > guess else "down"
    return label, closeness, direction
