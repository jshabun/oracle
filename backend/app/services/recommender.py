import pandas as pd
import numpy as np

DEFAULT_CATS = ["FG%","FT%","3PTM","PTS","REB","AST","STL","BLK","TO"]

def zscore_recommend(players: pd.DataFrame, punt=set(), needs=None):
    df = players.copy()
    cats = [c for c in DEFAULT_CATS if c not in punt]
    df_z = (df[cats] - df[cats].mean()) / df[cats].std(ddof=0)
    score = df_z.sum(axis=1)
    df["score"] = score
    df.sort_values("score", ascending=False, inplace=True)
    return df.head(20)