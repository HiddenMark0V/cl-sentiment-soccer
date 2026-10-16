def find_goal_candidates(df):
    pattern = r"\b(?:tor|treffer|ausgleich)\b"

    mask = df["text"].str.contains(
        pattern,
        case=False,
        na=False
    )

    return df.loc[mask].copy()
