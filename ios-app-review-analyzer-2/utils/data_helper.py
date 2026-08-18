import pandas as pd
from io import BytesIO

def load_csv(file_obj):
    df=pd.read_csv(file_obj,quoting=1,escapechar='\\')
    df.dropna(subset=["review"],inplace=True)
    return df

def export_csv(df):
    buffer=BytesIO()
    df.to_csv(buffer,index=False,encoding="utf‑8‑sig")
    buffer.seek(0)
    return buffer

def load_sample():
    return pd.read_csv("./data/sample_en.csv",quoting=1)
