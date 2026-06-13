# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**Feature implemented (Challenge 2):** a **Guess History sidebar** that lists every
past guess and visualizes how close each one was to the secret number.

**What task did you give the agent?**

I asked Claude (agent mode) to plan and implement a Guess History sidebar that,
for each previous guess, shows the guessed value, a "hot/cold" closeness
indicator with a progress bar, and which direction to move next. I asked it to
keep the closeness math in a pure, testable function rather than burying it in
the Streamlit UI code, and to add pytest cases for that function.

**What did the agent do?**

Files modified:
- `logic_utils.py` — added a pure `guess_proximity(guess, secret, low, high)`
  function returning `(label, closeness, direction)`. Closeness is normalized to
  the active difficulty range so it's clamped to `[0.0, 1.0]`.
- `app.py` — imported `guess_proximity` and added a "Guess History 📜" section to
  the sidebar that loops over `st.session_state.history`, renders each guess with
  its label + `st.sidebar.progress(closeness)` bar + a ⬆️/⬇️ direction, and flags
  invalid (non-number) guesses instead of scoring them.
- `tests/test_game_logic.py` — added 6 tests for `guess_proximity` (exact guess,
  direction up/down, closeness bounded in `[0,1]`, symmetry for equal distance,
  and range normalization).

Commands run: `python -m pytest tests/` to verify the suite (15 passed).

**What did you have to verify or fix manually?**

The agent's first version of the range-normalization test asserted the wrong
direction — it claimed a fixed distance of 10 should feel *warmer* on a narrow
range (1–20) than a wide one (1–100). pytest caught it: the implementation is
actually correct, because 10 out of 100 is a small fraction (closer) while 10 out
of 20 is half the board (farther). I rejected the AI's assertion, corrected the
test to expect `wide > narrow`, and re-ran the suite until all 15 passed. I also
confirmed the sidebar handles invalid guesses already stored in `history` (the
`isinstance(past_guess, int)` branch) so the proximity math never runs on a
non-number, and verified `app.py` still parses and the app launches.

The second correction came from running the app, not the tests. The agent first
rendered the sidebar inline near the top of `app.py`, but Streamlit reruns the
whole script top-to-bottom and the guess isn't appended to `history` until the
submit handler near the bottom — so the panel always lagged one guess behind
(my latest guess only appeared after I made the *next* one). I fixed this by
moving the rendering into a `render_guess_history()` function and calling it
*after* the submit handler appends the guess (plus once more before the
game-over `st.stop()` so the panel still shows on a finished board). This was the
same "Streamlit reruns top-to-bottom" lesson from the core bugs showing up again
in my own feature — a reminder that unit tests pass but you still have to *run*
a UI to catch ordering issues.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| | | | | |
| | | | | |
| | | | | |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
