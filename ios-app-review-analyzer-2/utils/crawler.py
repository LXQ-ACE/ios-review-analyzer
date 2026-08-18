import requests
import pandas as pd

def fetch_appstore_reviews(app_id,country="us",limit=50):
    url=f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"
    headers={
        "User‑Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    resp=requests.get(url,headers=headers,timeout=15)
    resp.raise_for_status()
    json_data=resp.json()
    entries=json_data["feed"]["entry"][1:]
    res_list=[]
    for item in entries:
        res_list.append({
            "review":item["content"]["label"],
            "rating":int(item["im:rating"]["label"])
        })
    df=pd.DataFrame(res_list[:limit])
    return df
