# :wave: Welcome to the quiz game based on football stats!

In this simple game your will be asked to predict the results of 5 football matches based on a subset of statistics provided for each match.

As such this is your chance to test your intuition on how predictive the football statistics are!

## Rules

For each match you will be provided with the following statistics per each team:
* a number of total shots attempted;
* a number of shots on target;
* cumulative expected goal probability of all shots (XG) - *think of this as the probabilistic estimate of the actual score*;
* possession percentage.

Based on that data you will need to predict how many goals were scored by each team.

**If you guess the result correctly (i.e. the draw or which team won) - you will get 1 point.**

**If you guess the result correctly and the number of goals scored by one team - you will receive 2 points.**

**If you guess the exact score - you will receive 3 points.**

## Data

<img src="assets/images/sblogo.svg" width=50% height=50%>

All the data used in this game is processed from publicly available resources provided by [StatsBomb](https://statsbomb.com/):

* [statsbombpy](https://github.com/statsbomb/statsbombpy)
* [open-data](https://github.com/statsbomb/open-data)

## Running in Docker

If you would like to host the app yourself, first clone the repo. Then inside the repo folder execute:

```bash
docker build -t streamlit -f docker/Dockerfile .
```

followed by

```
docker run -p 8501:8501 streamlit
```

The app will be available at http://localhost:8501