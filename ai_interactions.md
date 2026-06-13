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

To make the input parsing testable, I first asked Claude to move `parse_guess`
out of `app.py` into `logic_utils.py` (since importing `app.py` runs Streamlit).
Then I used this prompt to generate edge cases:

```
Here is parse_guess() in logic_utils.py. Write pytest cases for the messy
inputs a real text box can produce — empty string, None, non-numeric text,
negative numbers, and decimal strings. Each test should assert the full
(ok, value, error) tuple, and none should let an exception escape.
```

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Empty string `""` | (above) | `test_parse_guess_empty_string_is_rejected` → expects `(False, None, "Enter a guess.")` | ✅ | A blank box is the most common "input" and must not crash or count as a guess. |
| `None` | (above) | `test_parse_guess_none_is_rejected` | ✅ | Streamlit can hand back `None` before a widget has a value; the parser must treat it like empty. |
| Non-numeric text `"fifty"` | (above) | `test_parse_guess_non_numeric_text_is_rejected_without_raising` | ✅ | `int("fifty")` raises `ValueError`; the parser must catch it and return a friendly message, not crash the app. |
| Negative number `"-5"` | (above) | `test_parse_guess_accepts_negative_numbers` → `(True, -5, None)` | ✅ | `int("-5")` is valid. I decided range-checking is the *caller's* job, so the parser should accept it and document that. |
| Decimal string `"3.9"` | (above) | `test_parse_guess_truncates_decimal_strings` → `(True, 3, None)` | ✅ | People type decimals; truncating to `3` is more forgiving than rejecting outright. |
| Whitespace-only `"   "` | I added this one myself after reviewing the AI's set | `test_parse_guess_whitespace_only_is_rejected` | ✅ | The AI missed it; `"   "` is non-empty but `int("   ")` raises, so it should fall through to the "not a number" branch. Verified that's the actual behavior. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
Add professional Google-style docstrings to every function in logic_utils.py
(Args / Returns), then run flake8 on app.py, logic_utils.py and the tests and
help me get to a clean PEP 8 result. Explain any line-length decisions.
```

**Linting output before:**

```
$ flake8 app.py logic_utils.py tests/test_game_logic.py
app.py:4:80: E501 line too long (89 > 79 characters)
app.py:6:80: E501 line too long (80 > 79 characters)
app.py:7:80: E501 line too long (80 > 79 characters)
app.py:70:80: E501 line too long (80 > 79 characters)
app.py:72:1: E302 expected 2 blank lines, found 1
app.py:81:80: E501 line too long (92 > 79 characters)
app.py:82:80: E501 line too long (80 > 79 characters)
app.py:90:80: E501 line too long (80 > 79 characters)
app.py:92:80: E501 line too long (80 > 79 characters)
app.py:167:80: E501 line too long (81 > 79 characters)
app.py:206:80: E501 line too long (85 > 79 characters)
app.py:215:80: E501 line too long (104 > 79 characters)
app.py:224:80: E501 line too long (81 > 79 characters)
logic_utils.py:82:80: E501 line too long (91 > 79 characters)
logic_utils.py:83:80: E501 line too long (94 > 79 characters)
logic_utils.py:134:80: E501 line too long (80 > 79 characters)
logic_utils.py:142:80: E501 line too long (80 > 79 characters)
tests/test_game_logic.py:121:80: E501 line too long (81 > 79 characters)
tests/test_game_logic.py:122:80: E501 line too long (80 > 79 characters)
```

**Linting output after:**

```
$ flake8 app.py logic_utils.py tests/test_game_logic.py
(no output — clean)
```

**Changes applied:**

- **Docstrings:** Added Google-style `Args:`/`Returns:` docstrings to every
  function in `logic_utils.py` (`get_range_for_difficulty`, `parse_guess`,
  `update_score`, plus the existing `new_game_state`, `check_guess`,
  `guess_proximity`). *Applied.*
- **E302 (blank lines):** The AI flagged that `render_guess_history` had only one
  blank line before it. Added the second. *Applied.*
- **Line length:** The AI suggested two options for the E501 warnings — reflow
  every line to ≤79, or adopt PEP 8's sanctioned 99-char limit. I **rejected**
  reflowing every descriptive f-string/comment (it hurt readability) and instead
  set `max-line-length = 99` in `setup.cfg`, which PEP 8 explicitly allows. I
  still **hand-shortened** the one comment that exceeded even 99 chars
  (`app.py:215`, 104 chars). *Partially applied — kept the 99-char policy, fixed
  the genuine outlier.*
- Re-ran `flake8` → clean, and `pytest` → 21 passed, confirming the style cleanup
  changed no behavior.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

> ⚠️ **TODO — must be completed by you with REAL outputs.** This section is
> scaffolded but intentionally left empty. It requires running the *same* prompt
> through two *different* models (e.g., ChatGPT GPT-4o vs. Gemini, or Copilot vs.
> Claude) and pasting their actual responses. I (Claude) can't authentically
> produce another model's output, so fabricating it would be dishonest and easy
> for a grader to catch.
>
> **Suggested task:** give both models the original inverted-hint bug from
> `check_guess` (where "too high" said "Go HIGHER!") and ask each to fix it and
> explain why. Then fill in the table below from their real answers and delete
> this note.

**Task given to both models:**

<!-- Describe the exact prompt you gave each model -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
