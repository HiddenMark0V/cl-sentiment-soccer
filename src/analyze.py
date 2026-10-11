import pandas as pd


def make_goal_windows(df, goals):
    windows = []

    for i, goal in goals.iterrows():
        window = df[
            (df["match_id"] == goal["match_id"]) &
            (df["half"] == goal["half"])
        ].copy()

        window["relative_seconds"] = (
            window["time_mid"] - goal["goal_time"]
        )

        window = window[
            window["relative_seconds"].between(-300, 300)
        ].copy()

        window["goal_id"] = i + 1
        window["goal_time"] = goal["goal_time"]

        windows.append(window)

    return pd.concat(windows, ignore_index=True)