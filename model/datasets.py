import pandas as pd

def load_dataset(file_name: str) -> pd.DataFrame:
    return pd.read_csv(file_name)