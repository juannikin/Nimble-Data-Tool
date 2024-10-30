import pandas as pd
from typing import Dict, List
from datetime import datetime
import pytz
import logging
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_profile_activity(response_data: Dict) -> pd.DataFrame:
    """Process profile activity data into a pandas DataFrame"""
    activities = []
    
    for activity in response_data.get("activity", []):
        author = activity.get("author", {})
        
        # Handle created_at datetime conversion with null check
        created_at = activity.get("created_at")
        if created_at:
            try:
                created_at = pd.to_datetime(created_at)
                if created_at.tzinfo is None:
                    created_at = created_at.tz_localize('UTC')
                else:
                    created_at = created_at.tz_convert('UTC')
            except (ValueError, TypeError):
                created_at = None
                logger.warning(f"Failed to parse datetime: {activity.get('created_at')}")
        else:
            created_at = None
        
        activity_dict = {
            "author_name": author.get("title"),
            "author_occupation": author.get("occupation"),
            "author_image": author.get("image_url"),
            "author_url": author.get("url"),
            "post_text": activity.get("text"),
            "created_at": created_at,
            "post_url": activity.get("url")
        }
        activities.append(activity_dict)
    
    return pd.DataFrame(activities)

def filter_data(df: pd.DataFrame, 
                start_date: datetime = None,
                end_date: datetime = None,
                search_text: str = None) -> pd.DataFrame:
    """Filter DataFrame based on date and text search"""
    filtered_df = df.copy()
    
    logger.info(f"Initial data size: {len(filtered_df)}")
    logger.info(f"Filtering parameters - Start date: {start_date}, End date: {end_date}")
    
    # Handle date filtering only for non-null created_at values
    if 'created_at' in filtered_df.columns:
        # Create a mask for non-null dates
        date_mask = filtered_df['created_at'].notna()
        logger.info(f"Records with valid dates: {date_mask.sum()}")
        
        if start_date:
            # Convert start_date to UTC timezone if needed
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=pytz.UTC)
            else:
                start_date = start_date.astimezone(pytz.UTC)
            # Update mask for start date
            date_mask &= (filtered_df['created_at'] >= start_date)
            logger.info(f"Records after start date filter: {date_mask.sum()}")
        
        if end_date:
            # Convert end_date to UTC timezone if needed
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=pytz.UTC)
            else:
                end_date = end_date.astimezone(pytz.UTC)
            # Update mask for end date
            date_mask &= (filtered_df['created_at'] <= end_date)
            logger.info(f"Records after end date filter: {date_mask.sum()}")
        
        # Apply date filtering
        filtered_df = filtered_df[date_mask]
    
    if search_text:
        text_mask = (
            filtered_df['post_text'].str.contains(search_text, case=False, na=False) |
            filtered_df['author_name'].str.contains(search_text, case=False, na=False) |
            filtered_df['author_occupation'].str.contains(search_text, case=False, na=False)
        )
        filtered_df = filtered_df[text_mask]
        logger.info(f"Records after text search: {len(filtered_df)}")
    
    logger.info(f"Final filtered data size: {len(filtered_df)}")
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
    elif format == "excel":
        # Create a copy of the DataFrame to avoid modifying the original
        excel_df = df.copy()
        
        # Convert timezone-aware datetime to timezone-naive
        if 'created_at' in excel_df.columns:
            excel_df['created_at'] = excel_df['created_at'].dt.tz_localize(None)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            excel_df.to_excel(writer, index=False, sheet_name='LinkedIn Data')
        return output.getvalue()
    
    raise ValueError(f"Unsupported format: {format}")
