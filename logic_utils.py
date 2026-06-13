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


def get_range_for_difficulty(difficulty):
    """Return the inclusive ``(low, high)`` guess range for a difficulty.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.

    Returns:
        A ``(low, high)`` tuple: ``"Easy"`` -> ``(1, 20)``,
        ``"Normal"`` -> ``(1, 100)``, ``"Hard"`` -> ``(1, 50)``. Any
        unrecognized value falls back to ``(1, 100)``.
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw):
    """Parse raw user input into an integer guess.

    Handles the messy inputs a text box can produce: ``None``, an empty
    string, non-numeric text, and decimal strings (truncated toward zero,
    e.g. ``"3.9"`` -> ``3``). Negative numbers are accepted here; range
    validation is the caller's responsibility.

    Args:
        raw: The raw string (or ``None``) from the guess input box.

    Returns:
        A ``(ok, guess_int, error_message)`` tuple. On success,
        ``(True, <int>, None)``; on failure, ``(False, None, <message>)``.
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a number."

    return True, value, None


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


def update_score(current_score, outcome, attempt_number):
    """Return the new score after applying one guess outcome.

    Scoring rules (preserved from the original game logic):
      * ``"Win"`` awards ``100 - 10 * (attempt_number + 1)`` points, floored
        at a minimum of 10, so winning faster is worth more.
      * ``"Too High"`` adds 5 on even attempts and subtracts 5 otherwise.
      * ``"Too Low"`` subtracts 5.
      * Any other outcome leaves the score unchanged.

    Args:
        current_score: The score before this guess.
        outcome: One of ``"Win"``, ``"Too High"``, ``"Too Low"``.
        attempt_number: The 1-based attempt count for this guess.

    Returns:
        The updated score as an ``int``.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


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
