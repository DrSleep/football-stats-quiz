import base64
import typing as T
import warnings
from pathlib import Path

from statsbombpy import sb
from streamlit.state import AutoSessionState

warnings.filterwarnings("ignore", message="credentials were not supplied")


class SessionStateWithDefaults(AutoSessionState):
    def __init__(self, defaults, **kwargs):
        self._defaults = defaults
        super().__init__(**kwargs)
        self.reset()

    def reset(
        self, hard: bool = False, ignore: T.Optional[T.Union[str, T.List[str]]] = None
    ) -> None:
        if ignore is None:
            ignore = []
        elif isinstance(ignore, str):
            ignore = [ignore]
        assert isinstance(ignore, list)
        for k, v in self._defaults.items():
            if hard and k not in ignore:
                self[k] = v
            else:
                self.setdefault(k, v)


def get_match_info(match_id, comp_id, season_id):
    return sb.matches(comp_id, season_id).query(f"match_id == {match_id}")


def get_stats(match_id, home_team, away_team, off_target_shot_types, possession_types):
    all_events = sb.events(match_id=match_id)

    shots_events = all_events[all_events.type == "Shot"][
        ["shot_outcome", "shot_statsbomb_xg", "team"]
    ]
    possession_events = (
        all_events.query("duration > 0")
        .query(f"type in {possession_types}")
        .query("possession_team == team")
    )[["possession_team", "duration"]]

    shots_stats = get_shots_stats(
        shots_events, home_team, away_team, off_target_shot_types
    )
    possession_stats = get_possession_stats(possession_events, home_team, away_team)
    return {**shots_stats, **possession_stats}


def get_shots_stats(shots, home_team, away_team, off_target_shot_types):
    home_shots = shots[shots.team == home_team]
    away_shots = shots[shots.team == away_team]

    total_home_shots = len(home_shots)
    on_target_home_shots = len(
        home_shots[~home_shots.shot_outcome.isin(off_target_shot_types)]
    )
    xg_home_shots = home_shots.shot_statsbomb_xg.clip(0).sum()

    total_away_shots = len(away_shots)
    on_target_away_shots = len(
        away_shots[~away_shots.shot_outcome.isin(off_target_shot_types)]
    )
    xg_away_shots = away_shots.shot_statsbomb_xg.clip(0).sum()
    return {
        "total_shots": [total_home_shots, total_away_shots],
        "on_target_shots": [on_target_home_shots, on_target_away_shots],
        "shots_xg": [xg_home_shots, xg_away_shots],
    }


def get_possession_stats(possession, home_team, away_team):
    possession = (
        possession.groupby("possession_team", as_index=False)
        .agg({"duration": "sum"})
        .assign(possession=lambda x: x["duration"].div(x["duration"].sum()))
    )
    home_possession = possession[
        possession.possession_team == home_team
    ].possession.iloc[0]
    away_possession = possession[
        possession.possession_team == away_team
    ].possession.iloc[0]

    return {
        "possession": [home_possession, away_possession],
    }


def get_match_stats(
    match_id, comp_id, season_id, off_target_shot_types, possession_types
):
    match_info = get_match_info(match_id, comp_id, season_id)
    assert len(match_info) == 1
    match = match_info.iloc[0]

    home_team = match.home_team
    away_team = match.away_team

    home_goals, away_goals = match.home_score, match.away_score

    stats = get_stats(
        match_id, home_team, away_team, off_target_shot_types, possession_types
    )

    date = match.match_date
    competition = match.competition
    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "date": date,
        "competition": competition,
        **stats,
    }


def image_to_bytes(image_path: Path) -> str:
    return base64.b64encode((image_path).read_bytes()).decode()


def patch_markdown_image(image: str) -> str:
    image_path = Path(image)
    extension = image_path.suffix[1:].lower()  # [1:] to remove "." in ".ext"
    return f'<img src="data:image/{extension}+xml;base64,{image_to_bytes(image_path)}">'
