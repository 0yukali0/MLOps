import pandas as pd

def encode(s: pd.Series) -> pd.Series:
    unique_vals = pd.Series(s.unique())
    unique_vals = unique_vals.sort_values(na_position="last").reset_index(drop=True)
    mapping = {v: i for i, v in enumerate(unique_vals)}
    encoded = s.map(mapping)
    return encoded