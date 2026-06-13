import random
import streamlit as st

# FIX: Moved check_guess into logic_utils.py with Claude (agent mode) and import it here.
# FEATURE (Challenge 2): guess_proximity powers the Guess History sidebar.
# REFACTOR (Challenge 3): get_range_for_difficulty, parse_guess and update_score
# now live in logic_utils.py (single source of truth + unit-testable) instead of
# being duplicated here in app.py.
from logic_utils import (
    check_guess,
    new_game_state,
    guess_proximity,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# FIX: Added an input_nonce with Claude (agent mode) so the guess box can be
# reset by changing its widget key (Streamlit forbids editing a widget's value
# after it renders). Bumped on win/loss/New Game to clear the stale guess.
if "input_nonce" not in st.session_state:
    st.session_state.input_nonce = 0


# FEATURE (Challenge 2): Guess History sidebar. For each past guess, show its
# value, a hot/cold closeness label + bar, and which way to move next. Invalid
# (non-number) guesses are flagged instead of scored.
#
# FIX: This is defined as a function and CALLED later (after the submit handler
# appends the guess), not rendered inline here. Streamlit reruns top-to-bottom,
# and the guess isn't appended to history until the submit block near the bottom
# of the file — so rendering at this point would always lag one guess behind.
def render_guess_history():
    st.sidebar.divider()
    st.sidebar.subheader("Guess History 📜")
    if st.session_state.history:
        for i, past_guess in enumerate(st.session_state.history, start=1):
            if isinstance(past_guess, int):
                label, closeness, direction = guess_proximity(
                    past_guess, st.session_state.secret, low, high
                )
                arrow = {"up": "⬆️ go higher", "down": "⬇️ go lower", "hit": "✅"}[direction]
                st.sidebar.write(f"**{i}.** `{past_guess}` — {label} ({arrow})")
                st.sidebar.progress(closeness)
            else:
                st.sidebar.write(f"**{i}.** `{past_guess}` — ⚠️ not a number")
    else:
        st.sidebar.caption("No guesses yet. Make your first guess!")


# FEATURE (Challenge 4): Enhanced UI — a structured Session Summary table in the
# main area. Turns the raw history list into a readable recap (attempt number,
# guess, result, and hot/cold proximity) so the player can review the whole game
# at a glance instead of scrolling the sidebar. Like the sidebar, it's rendered
# AFTER the submit handler so the latest guess appears immediately.
def render_session_summary():
    if not st.session_state.history:
        return
    rows = []
    for i, past_guess in enumerate(st.session_state.history, start=1):
        if isinstance(past_guess, int):
            outcome, _ = check_guess(past_guess, st.session_state.secret)
            label, _, _ = guess_proximity(
                past_guess, st.session_state.secret, low, high
            )
            rows.append(
                {
                    "Attempt": i,
                    "Guess": str(past_guess),
                    "Result": outcome,
                    "Proximity": label,
                }
            )
        else:
            rows.append(
                {
                    "Attempt": i,
                    "Guess": str(past_guess),
                    "Result": "⚠️ Invalid",
                    "Proximity": "—",
                }
            )
    st.subheader("📊 Session Summary")
    st.table(rows)


st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    # FIX: Keyed the input on input_nonce with Claude (agent mode); a changed
    # key makes Streamlit build a fresh, empty box once the game ends.
    key=f"guess_input_{difficulty}_{st.session_state.input_nonce}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # FIX: Fixed the "New Game stuck" bug with Claude (agent mode). The old
    # handler only reset attempts/secret, leaving status="won"/"lost" (so the
    # next render hit st.stop()) and stale history, and hardcoded range 1-100.
    # Now delegates to new_game_state() and bumps input_nonce to clear the box.
    st.session_state.update(new_game_state(low, high))
    st.session_state.input_nonce += 1
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    # Render the history before stopping, otherwise the panel would be blank on
    # a finished board (st.stop() halts the rerun before the call at the bottom).
    render_guess_history()
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    render_session_summary()
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            # FIX: Bump input_nonce with Claude (agent mode) to clear the box on win.
            st.session_state.input_nonce += 1
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                # FIX: Bump input_nonce (Claude) to clear the box when out of attempts.
                st.session_state.input_nonce += 1
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# Render the sidebar history AND the main-area summary table AFTER the submit
# handler above has appended the new guess, so a guess shows up on the same click
# instead of one click late.
render_guess_history()
render_session_summary()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
