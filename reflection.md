# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?
The first time I ran the game it loaded and looked normal, but it was unplayable
once I actually tried to use it. The two bugs that stood out were: (1) the
hints were backwards — when my guess was too high it told me to go HIGHER, and
when it was too low it told me to go LOWER, so following the hints pushed me away
from the answer; and (2) the "New Game" button didn't seem to work — after a game
ended, clicking it left the board frozen on the "you already won / game over"
message, kept my old guesses in the history, and seemed to use the wrong number
range. Both made it impossible to play a clean round from start to finish.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Secret is 50, guess 60 (too high) | Hint says go LOWER | Hint said "📈 Go HIGHER!" (backwards) | No error — wrong message displayed |
| Win a game, then click "New Game 🔁" | Board resets to a fresh playable round | Board stayed frozen on "You already won. Start a new game", couldn't play | No error — `status` left as `"won"` so `st.stop()` ran |
| Click "New Game 🔁" after playing | History cleared and secret drawn from the active difficulty range | Old guesses still listed; secret always drawn from 1–100 even on Easy (1–20) / Hard (1–50) | No error — stale `history` and hardcoded `random.randint(1, 100)` |

---

## 2. How did you use AI as a teammate?

I used Claude (in agent mode) as my pair programmer. I had it help me locate the
backwards-hint logic and the broken "New Game" handler, and I asked it to refactor
`check_guess` out of `app.py` into `logic_utils.py` so the logic could be tested.

- **A suggestion that was correct:** Claude pointed out that the "New Game" button
  looked broken because the handler only reset `attempts` and `secret` but left
  `status` as `"won"`/`"lost"`, so the very next rerun hit `st.stop()` and froze
  the page. It suggested resetting `status` back to `"playing"` (and clearing
  `history`). I verified this by playing a full game, winning, clicking New Game,
  and confirming I could immediately start guessing again — and by writing
  `test_new_game_resets_status_to_playing`, which passed.

- **A suggestion that was misleading:** When I asked how to clear the guess input
  box after a game ended, Claude first suggested directly setting
  `st.session_state["guess_input_..."] = ""`. That actually throws a Streamlit
  error, because you can't modify a widget's value after it has been instantiated
  on the same run. I rejected that approach and instead changed the widget's
  `key` so Streamlit builds a fresh, empty box — which is the pattern that
  actually works.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed when I could both (a) reproduce the old broken
behavior in my head from the original code and (b) see the corrected behavior
in the running app *and* have an automated test lock it in. For the inverted
hints I wrote `test_too_high_tells_player_to_go_lower`, which asserts that a
too-high guess returns a message containing "LOWER" and *not* "HIGHER". That test
was useful because it would fail the moment someone swapped the messages back —
it shows the fix is the wrong-message bug specifically, not just "some message
appears." AI helped me design these tests: I asked Claude to suggest edge cases,
and it recommended testing the *message text* (not just the "Too High"/"Too Low"
label), which is what actually catches the swap bug. All 9 tests pass with
`python -m pytest tests/`.

---

## 4. What did you learn about Streamlit and state?

I'd explain it like this: every time you interact with a Streamlit app — click a
button, type in a box — Streamlit doesn't just update that one piece, it re-runs
your *entire* script from top to bottom. So any normal variable gets recreated
from scratch on every click, which is why the secret number kept "resetting."
`st.session_state` is a special dictionary that survives those reruns — it's the
app's memory between clicks. The trick is to only initialize a value if it isn't
already in `st.session_state`, so it persists; and when you want a real reset
(like New Game), you have to explicitly overwrite *all* the relevant state keys,
not just one or two.

---

## 5. Looking ahead: your developer habits

- **Habit I want to reuse:** Writing a small automated test the moment I fix a
  bug, instead of just eyeballing the app. Having `pytest` confirm the fix — and
  guard against it breaking later — made me far more confident than manual
  clicking alone, and it forced me to pull the logic into a testable function.

- **What I'd do differently:** I'd verify the AI's suggestions against the actual
  framework docs *before* pasting them in. The `session_state["guess_input"] = ""`
  suggestion looked reasonable but broke at runtime, and I lost time on it that a
  quick check would have saved.

- **How this changed my thinking:** I now treat AI-generated code as a confident
  draft from a teammate who is sometimes wrong — useful for speed and ideas, but
  something I have to read, run, and test before I trust it.
