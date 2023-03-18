import typing as T

import streamlit as st

from .dataset import StatsDataset
from .utils import SessionStateWithDefaults, patch_markdown_image


class StatsQuizGame:
    def __init__(
        self,
        session_state: SessionStateWithDefaults,
        start_button_placeholder: T.Any,
        scores_placeholder: T.Any,
        dataset: StatsDataset,
        max_examples: int = 5,
        sidebar_file: str = "README.md",
        sblogo: str = "./assets/images/sblogo.svg",
    ):
        self._session_state = session_state
        self._scores_placeholder = scores_placeholder
        self._start_button_placeholder = start_button_placeholder
        self._dataset = dataset
        self._max_examples = max_examples
        self._sidebar_file = sidebar_file
        self._sblogo = sblogo

    def run(self) -> None:
        self._sidebar()
        self._start_button_placeholder.button(
            "Start the game", on_click=self._on_game_start
        )
        self._main()

    def _sidebar(self) -> None:
        with st.sidebar, open(self._sidebar_file, "r", encoding="utf8") as f:
            # NOTE(Vladimir): Streamlit is unable to render the images in the
            # markdown. We will explicitly convert the SB logo to bytes here.
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "img src=" in line:
                    line = patch_markdown_image(self._sblogo)
                    lines[i] = line
                    break
            st.markdown("".join(lines), unsafe_allow_html=True)

    def _on_game_start(self):
        self._session_state.reset(hard=True, ignore="best_score")
        self._session_state.started = True
        self._load_next_sample()

    def _load_next_sample(self):
        self._session_state.sample = next(self._dataset)
        self._session_state.display_next_button = False

    def _main(self):
        if not self._session_state.started:
            return
        self._start_button_placeholder.empty()

        with self._scores_placeholder:
            self._display_scores()

        left, right = st.columns(2)

        with right:
            self._display_stats_data(self._session_state.sample[1])

        if self._session_state.display_next_button or self._session_state.finished:
            with right:
                # After submitting the form, we show extra available information
                self._display_stats_data(self._session_state.sample[2])

            with left.container():
                self._display_results()

            if self._session_state.display_next_button:
                self._start_button_placeholder.button(
                    "Next", on_click=self._load_next_sample
                )

            if self._session_state.finished:
                self._start_button_placeholder.button(
                    "Start a new game", on_click=self._on_game_start
                )
                return

        else:
            with left:
                with st.form(key="quiz", clear_on_submit=True):
                    st.number_input(
                        "Home team goals",
                        key="home_team_goals",
                        min_value=0,
                        max_value=999,
                    )
                    st.number_input(
                        "Away team goals",
                        key="away_team_goals",
                        min_value=0,
                        max_value=999,
                    )
                    st.form_submit_button(
                        "Submit", on_click=self._on_submit_predictions
                    )

    def _display_stats_data(self, stats):
        markdown = "### " + (
            f'<div class="statsData"><span> {"<br><br>".join(stats)} </span></div>'
        )
        st.markdown(markdown, unsafe_allow_html=True)

    def _display_results(self):
        home_gt, away_gt = self._session_state.sample[0]
        lines = []
        lines.append(
            f":bulb: Predicted: {self._session_state.htg} - {self._session_state.atg}"
        )
        lines.append(f":goal_net: Actual Score: {home_gt} - {away_gt}")
        points = self._session_state.current_score
        if points == 0:
            points_emoji = ":x:"
        elif points == 1:
            points_emoji = ":heavy_exclamation_mark:"
        elif points == 2:
            points_emoji = ":interrobang:"
        elif points == 3:
            points_emoji = ":bangbang:"
        lines.append(f"{points_emoji} Points: {points}")

        markdown = "### " + (
            f'<div class="boxResults"><span> {"<br>".join(lines)} </span></div>'
        )
        st.markdown(markdown, unsafe_allow_html=True)

    def _display_scores(self):
        lines = [
            f":100: Total points: {self._session_state.total_score}",
            f":trophy: Best score: {self._session_state.best_score}",
            f":chart_with_upwards_trend: Done: {self._session_state.index}/{self._max_examples}",
        ]
        markdown = "### " + (
            f'<div class="scoresData"><span> {"&ensp;".join(lines)} </span></div>'
        )
        st.markdown(markdown, unsafe_allow_html=True)

    def _on_submit_predictions(self):
        self._session_state.htg = self._session_state.home_team_goals
        self._session_state.atg = self._session_state.away_team_goals
        self._session_state.index += 1

        if self._session_state.index < self._max_examples:
            self._session_state.display_next_button = True
        else:
            self._session_state.finished = True

        self._session_state.current_score = self._dataset.compute_score(
            self._session_state.sample[0],
            self._session_state.htg,
            self._session_state.atg,
        )
        self._session_state.total_score += self._session_state.current_score
        self._session_state.best_score = max(
            self._session_state.best_score, self._session_state.total_score
        )
