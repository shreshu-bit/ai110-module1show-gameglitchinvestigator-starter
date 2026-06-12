from logic_utils import check_guess, new_game_state


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, outcome should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, outcome should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Targets the high/low message swap bug ---
# FIX: Added these tests with Claude (agent mode) to lock in the hint-swap fix.
# When the guess is too high the player must go LOWER, and when the guess
# is too low the player must go HIGHER. The bug had these messages reversed.

def test_too_high_tells_player_to_go_lower():
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message.upper()
    assert "HIGHER" not in message.upper()


def test_too_low_tells_player_to_go_higher():
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message.upper()
    assert "LOWER" not in message.upper()


# --- Targets the "New Game stuck" bug (app.py New Game button) ---
# FIX: Added these tests with Claude (agent mode) after extracting the reset
# into logic_utils.new_game_state() so the previously-untestable handler logic
# could be locked in.
# The original handler only reset attempts and secret. It left status as
# "won"/"lost" (so the next render hit st.stop() and the game stayed stuck),
# left the previous guesses in history, and hardcoded random.randint(1, 100)
# instead of honoring the difficulty's (low, high) range.

def test_new_game_resets_status_to_playing():
    # A finished game left status as "won"/"lost"; New Game must clear it.
    state = new_game_state(1, 100)
    assert state["status"] == "playing"


def test_new_game_clears_history():
    state = new_game_state(1, 100)
    assert state["history"] == []


def test_new_game_resets_attempts():
    state = new_game_state(1, 100)
    assert state["attempts"] == 0


def test_new_game_uses_difficulty_range_not_hardcoded_1_100():
    # Hard difficulty is 1..50. The bug hardcoded 1..100, so the secret could
    # land outside the active range. Spy on the rng to lock the bounds in.
    calls = []

    def fake_randint(low, high):
        calls.append((low, high))
        return low

    new_game_state(1, 50, rng=fake_randint)
    assert calls == [(1, 50)]
