# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.** A Streamlit number-guessing game. The app
  picks a secret number inside a range that depends on the chosen difficulty
  (Easy 1–20, Normal 1–100, Hard 1–50). You type a guess, the game tells you
  whether to go higher or lower, tracks your attempts and score, and ends when
  you guess correctly or run out of attempts.

- [x] **Detail which bugs you found.**
  1. **Inverted hints (logic bug).** When a guess was *too high*, the game said
     "📈 Go HIGHER!" and when it was *too low* it said "📉 Go LOWER!" — both
     backwards, so following the hints moved you away from the answer.
  2. **"New Game" stuck (state bug).** Clicking **New Game 🔁** after a game
     ended appeared to do nothing: the board stayed frozen on "You already won"
     / "Game over", old guesses were still listed in the history, and the secret
     was always drawn from 1–100 even on Easy/Hard difficulties.

- [x] **Explain what fixes you applied.**
  1. Moved `check_guess` out of `app.py` into [logic_utils.py](logic_utils.py)
     and swapped the two hint messages so *too high → "Go LOWER!"* and
     *too low → "Go HIGHER!"*.
  2. Extracted the New Game reset into a pure, testable
     [`new_game_state()`](logic_utils.py#L7) function that resets `attempts`,
     clears `history`, sets `status` back to `"playing"` (the missing reset that
     was freezing the board), and draws the secret from the active
     `(low, high)` range instead of a hardcoded 1–100.

## 📸 Demo Walkthrough

A sample game on **Normal** difficulty (range 1–100), where the secret is **63**:

1. App loads. The info banner shows the range (1–100) and attempts left, and the
   guess box is empty.
2. User enters **40** and clicks **Submit Guess 🚀** → game returns **"Too Low"**
   with the hint **"📈 Go HIGHER!"**.
3. User enters **80** → game returns **"Too High"** with the hint
   **"📉 Go LOWER!"** (hints now point the right way).
4. User enters **63** → game returns **"🎉 Correct!"**, balloons appear, and it
   shows the winning message with the final score.
5. The score updates after each guess, and once the game is won the board locks
   until **New Game 🔁** is clicked, which clears the history and starts a fresh
   round in the correct difficulty range.

## 🧪 Test Results

```
$ python -m pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0
collected 21 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  4%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  9%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 14%]
tests/test_game_logic.py::test_too_high_tells_player_to_go_lower PASSED  [ 19%]
tests/test_game_logic.py::test_too_low_tells_player_to_go_higher PASSED  [ 23%]
tests/test_game_logic.py::test_new_game_resets_status_to_playing PASSED  [ 28%]
tests/test_game_logic.py::test_new_game_clears_history PASSED            [ 33%]
tests/test_game_logic.py::test_new_game_resets_attempts PASSED           [ 38%]
tests/test_game_logic.py::test_new_game_uses_difficulty_range_not_hardcoded_1_100 PASSED [ 42%]
tests/test_game_logic.py::test_proximity_exact_guess_is_full_closeness_and_hit PASSED [ 47%]
tests/test_game_logic.py::test_proximity_points_up_when_secret_is_higher PASSED [ 52%]
tests/test_game_logic.py::test_proximity_points_down_when_secret_is_lower PASSED [ 57%]
tests/test_game_logic.py::test_proximity_closeness_stays_between_0_and_1 PASSED [ 61%]
tests/test_game_logic.py::test_proximity_is_symmetric_for_equal_distance PASSED [ 66%]
tests/test_game_logic.py::test_proximity_is_normalized_to_range PASSED   [ 71%]
tests/test_game_logic.py::test_parse_guess_empty_string_is_rejected PASSED [ 76%]
tests/test_game_logic.py::test_parse_guess_none_is_rejected PASSED       [ 80%]
tests/test_game_logic.py::test_parse_guess_non_numeric_text_is_rejected_without_raising PASSED [ 85%]
tests/test_game_logic.py::test_parse_guess_accepts_negative_numbers PASSED [ 90%]
tests/test_game_logic.py::test_parse_guess_truncates_decimal_strings PASSED [ 95%]
tests/test_game_logic.py::test_parse_guess_whitespace_only_is_rejected PASSED [100%]

============================== 21 passed in 0.01s ===============================
```

The last six cases are **advanced edge-case tests** for `parse_guess` (empty string,
`None`, non-numeric text, negative numbers, decimal strings, whitespace-only). See
[ai_interactions.md](ai_interactions.md) for the prompts and rationale.

## 🚀 Stretch Features

- [x] **Challenge 2 — Feature Expansion: Guess History sidebar.** Added a
  "Guess History 📜" panel in the sidebar that lists every past guess with a
  hot/cold closeness indicator (🔥/🌡️/😎/❄️), a progress bar showing how near it
  was to the secret, and a ⬆️/⬇️ hint for which way to move next. The closeness
  math lives in a pure, unit-tested `guess_proximity()` in
  [logic_utils.py](logic_utils.py); see [ai_interactions.md](ai_interactions.md)
  for the agent workflow.
- [x] **Challenge 1 — Advanced Edge-Case Testing.** Added six pytest cases for
  `parse_guess` covering empty input, `None`, non-numeric text, negative numbers,
  decimal strings, and whitespace-only. To make this testable, `parse_guess` (plus
  `get_range_for_difficulty` and `update_score`) were moved out of `app.py` into
  [logic_utils.py](logic_utils.py) as a single source of truth. Full passing output
  is in the [Test Results](#-test-results) block above.

- [x] **Challenge 3 — Professional Documentation & Style.** Added Google-style
  docstrings to every function in [logic_utils.py](logic_utils.py) and brought the
  code to PEP 8 (clean `flake8`, configured in [setup.cfg](setup.cfg)). The prompts,
  the before/after linting output, and which suggestions were applied are recorded
  in [ai_interactions.md](ai_interactions.md).

- [x] **Challenge 4 — Enhanced Game UI.** Two structured UI upgrades make the game
  easier to follow:
  - A **📊 Session Summary table** in the main area (`render_session_summary()` in
    [app.py](app.py)) recapping every attempt with its number, guess, result, and
    hot/cold proximity.
  - **Emoji hot/cold states and progress bars** in the Guess History sidebar
    (`render_guess_history()`), plus the guess prompt now shows the *actual*
    difficulty range (e.g. "between 1 and 20" on Easy) instead of a hardcoded
    "1 and 100".

  These improve readability without changing core game logic.
