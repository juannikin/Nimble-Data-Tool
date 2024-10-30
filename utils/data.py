import pandas as pd
from typing import Dict, List

def process_profile_activity(response_data: Dict) -> pd.DataFrame:
    """Process profile activity data into a pandas DataFrame"""
    activities = []
    
    for activity in response_data.get("activity", []):
        metrics = activity.get("metrics", {})
        author = activity.get("author", {})
        
        activity_dict = {
            "author_name": author.get("title"),
            "author_occupation": author.get("occupation"),
            "author_image": author.get("image_url"),
            "author_url": author.get("url"),
            "post_text": activity.get("text"),
            "created_at": activity.get("created_at"),
            "shares": metrics.get("shares", 0),
            "comments": metrics.get("comments", 0),
            "likes": metrics.get("likes", 0),
            "reactions": metrics.get("reactions", {}),
            "post_url": activity.get("url")
        }
        activities.append(activity_dict)
    
    return pd.DataFrame(activities)

def format_for_download(df: pd.DataFrame, format: str) -> bytes:
    """Format DataFrame for download"""
    if format == "csv":
        return df.to_csv(index=False).encode('utf-8')
    elif format == "json":
        return df.to_json(orient="records").encode('utf-8')
    raise ValueError(f"Unsupported format: {format}")
