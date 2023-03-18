import pickle
import random
import typing as T
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np

from .utils import get_match_stats


class StatsDataset(ABC):
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        ...

    def _format_data(
        self,
        home_team,
        away_team,
        home_goals,
        away_goals,
        **kwargs,
    ):
        # This data is what will be displayed to the user at first
        user_data = []
        if (total_shots := kwargs.get("total_shots", None)) is not None:
            user_data.append(self._format_total_shots(total_shots))
        if (on_target_shots := kwargs.get("on_target_shots", None)) is not None:
            user_data.append(self._format_on_target_shots(on_target_shots))
        if (shots_xg := kwargs.get("shots_xg", None)) is not None:
            user_data.append(self._format_shots_xg(shots_xg))
        if (possession := kwargs.get("possession", None)) is not None:
            user_data.append(self._format_possession(possession))

        # This is the ground truth data
        score = [home_goals, away_goals]

        # This is extra metadata that we will show to the user after
        # they submitted their guess
        user_extra_data = [
            f":checkered_flag: {home_team} - {away_team}",
        ]
        if (date := kwargs.get("date", None)) is not None:
            user_extra_data.append(self._format_date(date))
        if (competition := kwargs.get("competition", None)) is not None:
            user_extra_data.append(self._format_competition(competition))

        return score, user_data, user_extra_data

    @staticmethod
    def _format_total_shots(total_shots: T.List[int]) -> str:
        return f":soccer: Total shots: {total_shots[0]:d} - {total_shots[1]:d}"

    @staticmethod
    def _format_on_target_shots(on_target_shots: T.List[int]) -> str:
        return (
            f":dart: On target shots: {on_target_shots[0]:d} - {on_target_shots[1]:d}"
        )

    @staticmethod
    def _format_shots_xg(shots_xg: T.List[int]) -> str:
        return f":game_die: Shots XG: {shots_xg[0]:.3f} - {shots_xg[1]:.3f}"

    @staticmethod
    def _format_possession(possession: T.List[int]) -> str:
        return f":bar_chart: Possession: {possession[0]*100.0:.1f} - {possession[1]*100:.1f}"

    @staticmethod
    def _format_date(date: str) -> str:
        return f":calendar: {date}"

    @staticmethod
    def _format_competition(competition: str) -> str:
        return f":globe_with_meridians: {competition}"

    @staticmethod
    def compute_score(score_gt, home_prediction, away_prediction):
        home_gt, away_gt = score_gt
        points = 0
        if np.sign(home_gt - away_gt) == np.sign(home_prediction - away_prediction):
            points += 1
            if home_gt == home_prediction:
                points += 1
            if away_gt == away_prediction:
                points += 1
        return points


class DummyStatsDataset(StatsDataset):
    def __next__(self):
        total_home_shots = random.randint(0, 19)
        total_away_shots = random.randint(0, 19)
        on_target_home_shots = random.randint(0, total_home_shots)
        on_target_away_shots = random.randint(0, total_away_shots)
        home_goals = random.randint(0, on_target_home_shots)
        away_goals = random.randint(0, on_target_away_shots)
        home_team = "Barcelona"
        away_team = "Liverpool"
        date = f"{random.randint(1, 28)}/{random.randint(1,12)}/{random.randint(2000,2023)}"
        competition = "Champions League"
        return self._format_data(
            home_team,
            away_team,
            home_goals,
            away_goals,
            total_shots=[total_home_shots, total_away_shots],
            on_target_shots=[on_target_home_shots, on_target_away_shots],
            date=date,
            competition=competition,
        )


class SBStatsDataset(StatsDataset):
    def __init__(
        self,
        off_target_shot_types=(
            "Off T",
            "Blocked",
            "Wayward",
            "Saved Off Target",
        ),
        possession_types=(
            "50/50",
            "Ball Recovery",
            "Carry",
            "Clearance",
            "Dribble",
            "Duel",
            "Foul Won",
            "Goal Keeper",
            "Interception",
            "Pass",
            "Shield",
            "Shot",
        ),
        data_dir: Path = Path("./data/"),
        overwrite: bool = False,
        metafile: str = "ids.npy",
    ):
        self._off_target_shot_types = off_target_shot_types
        self._possession_types = possession_types
        self._ids_n3 = np.load(data_dir / metafile)  # [[match_id, comp_id, season_id]])
        self._data_dir = data_dir
        self._overwrite = overwrite
        self._indices = np.arange(len(self._ids_n3))
        self._reset()

    def _reset(self):
        self._i = -1
        random.shuffle(self._indices)

    def __next__(self):
        if self._i == (len(self._indices) - 1):
            self._reset()
        self._i += 1
        match_id, comp_id, season_id = self._ids_n3[self._indices[self._i]]
        if (
            match_stats_file := self._data_dir / f"{match_id}.pickle"
        ).exists() and not self._overwrite:
            with open(match_stats_file, "rb") as f:
                match_stats = pickle.load(f)
        else:
            match_stats = get_match_stats(
                match_id,
                comp_id,
                season_id,
                self._off_target_shot_types,
                self._possession_types,
            )
            with open(match_stats_file, "wb") as f:
                pickle.dump(match_stats, f)
        return self._format_data(**match_stats)
