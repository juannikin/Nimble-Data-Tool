import pandas as pd
from typing import Dict, List
from datetime import datetime
import pytz

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
            "created_at": pd.to_datetime(activity.get("created_at")).tz_convert('UTC'),
            "shares": metrics.get("shares", 0),
            "comments": metrics.get("comments", 0),
            "likes": metrics.get("likes", 0),
            "total_engagement": metrics.get("shares", 0) + metrics.get("comments", 0) + metrics.get("likes", 0),
            "reactions": metrics.get("reactions", {}),
            "post_url": activity.get("url")
        }
        activities.append(activity_dict)
    
    return pd.DataFrame(activities)

def filter_data(df: pd.DataFrame, 
                start_date: datetime = None,
                end_date: datetime = None,
                min_engagement: int = None,
                search_text: str = None) -> pd.DataFrame:
    """Filter DataFrame based on various criteria"""
    filtered_df = df.copy()
    
    # Ensure DataFrame's created_at column is in UTC
    if 'created_at' in filtered_df.columns:
        filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at']).dt.tz_convert('UTC')
    
    if start_date:
        # Convert start_date to UTC timezone
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=pytz.UTC)
        else:
            start_date = start_date.astimezone(pytz.UTC)
        filtered_df = filtered_df[filtered_df['created_at'] >= start_date]
    
    if end_date:
        # Convert end_date to UTC timezone
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=pytz.UTC)
        else:
            end_date = end_date.astimezone(pytz.UTC)
        filtered_df = filtered_df[filtered_df['created_at'] <= end_date]
    
    if min_engagement is not None:
        filtered_df = filtered_df[filtered_df['total_engagement'] >= min_engagement]
    
    if search_text:
        text_mask = (
            filtered_df['post_text'].str.contains(search_text, case=False, na=False) |
            filtered_df['author_name'].str.contains(search_text, case=False, na=False) |
            filtered_df['author_occupation'].str.contains(search_text, case=False, na=False)
        )
        filtered_df = filtered_df[text_mask]
    
    return filtered_df

def sort_data(df: pd.DataFrame, sort_by: str, ascending: bool = False) -> pd.DataFrame:
    """Sort DataFrame by specified column"""
    if sort_by in df.columns:
        return df.sort_values(by=sort_by, ascending=ascending)
    return df

def format_for_download(df: pd.DataFrame, format: str) -> bytes:
    """Format DataFrame for download"""
    if format == "csv":
        return df.to_csv(index=False).encode('utf-8')
    elif format == "json":
        return df.to_json(orient="records").encode('utf-8')
    raise ValueError(f"Unsupported format: {format}")
