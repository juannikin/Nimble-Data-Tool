import streamlit as st
from utils.api import NimbleAPI
from utils.data import process_profile_activity, format_for_download
from utils.ui import setup_page, create_metrics_chart, create_reactions_chart, display_profile_card

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
                    
                    # Display Results
                    for _, row in df.iterrows():
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
                        st.markdown(f"*Posted on: {row['created_at']}*")
                        
                        # Metrics Visualization
                        col1, col2 = st.columns(2)
                        with col1:
                            metrics_fig = create_metrics_chart({
                                "likes": row["likes"],
                                "comments": row["comments"],
                                "shares": row["shares"]
                            })
                            st.plotly_chart(metrics_fig, use_container_width=True)
                        
                        with col2:
                            reactions_fig = create_reactions_chart(row["reactions"])
                            st.plotly_chart(reactions_fig, use_container_width=True)
                    
                    # Download Options
                    if not df.empty:
                        st.markdown("### Download Data")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            csv = format_for_download(df, "csv")
                            st.download_button(
                                "Download CSV",
                                csv,
                                "linkedin_data.csv",
                                "text/csv"
                            )
                        
                        with col2:
                            json = format_for_download(df, "json")
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
