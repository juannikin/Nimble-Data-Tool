import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import logging
from utils.api import NimbleAPI
from utils.data import process_profile_activity, format_for_download, filter_data, sort_data
from utils.ui import setup_page, display_profile_card

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    setup_page()
    
    # Sidebar
    with st.sidebar:
        st.title("Nimble")
        st.markdown("### LinkedIn Data Pipeline")
        
        # API Key Input
        api_key = st.text_input("Enter API Key", type="password")
        
        # Template Selection
        template = st.selectbox(
            "Select Template",
            ["LinkedIn Profile Scraper", "LinkedIn Company Page Scraper"]
        )
        
        # Advanced Filtering Options
        st.markdown("### Advanced Filters")
        
        # Date Range Filter
        st.markdown("#### Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                datetime.now(pytz.UTC) - timedelta(days=30)
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                datetime.now(pytz.UTC)
            )
        
        # Text Search
        search_text = st.text_input(
            "Search Text",
            help="Search in post content, author name, and occupation"
        )
        
        # Sorting Options
        st.markdown("#### Sort By")
        sort_by = st.selectbox(
            "Sort Posts By",
            ["created_at"]
        )
        sort_order = st.radio(
            "Sort Order",
            ["Descending", "Ascending"]
        )
    
    # Main Content
    if not api_key:
        st.warning("Please enter your Nimble API key to continue.")
        return
    
    api = NimbleAPI(api_key)
    
    # URL Input Section
    st.header("Data Input")
    urls_input = st.text_area(
        "Enter LinkedIn URLs (one per line)",
        height=100,
        help="Enter the LinkedIn profile or company URLs you want to analyze"
    )
    
    if urls_input and st.button("Fetch Data"):
        try:
            urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
            
            with st.spinner("Fetching data..."):
                if template == "LinkedIn Profile Scraper":
                    response_data = api.get_profile_activity(urls)
                    df = process_profile_activity(response_data)
                    
                    logger.info(f"Initial dataset size: {len(df)}")
                    
                    # Create timezone-aware datetime objects for filtering
                    start_datetime = pytz.UTC.localize(
                        datetime.combine(
                            start_date,
                            datetime.min.time().replace(hour=0, minute=0, second=0)
                        )
                    )
                    
                    end_datetime = pytz.UTC.localize(
                        datetime.combine(
                            end_date,
                            datetime.min.time().replace(hour=23, minute=59, second=59)
                        )
                    )
                    
                    # Apply filters
                    filtered_df = filter_data(
                        df,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        search_text=search_text
                    )
                    
                    # Apply sorting
                    sorted_df = sort_data(
                        filtered_df,
                        sort_by,
                        ascending=(sort_order == "Ascending")
                    )
                    
                    # Display total posts metric
                    st.metric("Total Posts", len(sorted_df))
                    
                    # Display Results
                    st.markdown("### Posts")
                    for _, row in sorted_df.iterrows():
                        st.markdown("---")
                        
                        # Profile Information
                        author = {
                            "title": row["author_name"],
                            "occupation": row["author_occupation"],
                            "image_url": row["author_image"],
                            "url": row["author_url"]
                        }
                        display_profile_card(author)
                        
                        # Post Content
                        st.markdown(f"**Post:**\n{row['post_text']}")
                        if pd.notnull(row['created_at']):
                            st.markdown(f"*Posted on: {row['created_at'].strftime('%Y-%m-%d %H:%M:%S %Z')}*")
                        else:
                            st.markdown("*Posted on: Date not available*")
                    
                    # Download Options
                    if not sorted_df.empty:
                        st.markdown("### Download Data")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            csv = format_for_download(sorted_df, "csv")
                            st.download_button(
                                "Download CSV",
                                csv,
                                "linkedin_data.csv",
                                "text/csv"
                            )
                        
                        with col2:
                            json = format_for_download(sorted_df, "json")
                            st.download_button(
                                "Download JSON",
                                json,
                                "linkedin_data.json",
                                "application/json"
                            )
                
                else:
                    st.info("Company Page Scraper functionality coming soon!")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
