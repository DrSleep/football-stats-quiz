"""Streamlit app entry

Run with

```
streamlit run app.py
````

"""
import streamlit as st

from stats_quiz_game.dataset import SBStatsDataset, StatsDataset
from stats_quiz_game.stats_quiz_game import StatsQuizGame
from stats_quiz_game.utils import SessionStateWithDefaults


@st.cache(allow_output_mutation=True)
def create_dataset() -> StatsDataset:
    return SBStatsDataset()


if __name__ == "__main__":
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="collapsed"
        if st.session_state.get("started", False)
        else "expanded",
        page_icon="assets/images/logo.png",
        page_title="Football Stats Quiz",
    )
    with open("assets/html/style.html", "r", encoding="utf8") as f:
        st.markdown(
            f.read(),
            unsafe_allow_html=True,
        )

    scores_placeholder = st.columns([1, 5, 1])[1].empty()
    start_button_placeholder, all_scores_button_placeholder = st.empty(), st.empty()

    game = StatsQuizGame(
        session_state=SessionStateWithDefaults(
            defaults={
                "started": False,
                "sample": ([], [], []),
                "display_next_button": False,
                "finished": False,
                "htg": -1,
                "atg": -1,
                "index": 0,
                "current_score": 0,
                "total_score": 0,
                "best_score": 0,
                "per_round_scores": [],
                "showing_per_round_scores": False,
            },
        ),
        start_button_placeholder=start_button_placeholder,
        all_scores_button_placeholder=all_scores_button_placeholder,
        scores_placeholder=scores_placeholder,
        dataset=create_dataset(),
    )
    game.run()
