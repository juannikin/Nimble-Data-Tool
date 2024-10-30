import requests
from typing import Dict, List, Optional

class NimbleAPI:
    BASE_URL = "https://social.webit.live/linkedin/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
    
    def get_profile_activity(self, linkedin_urls: List[str]) -> Dict:
        """Fetch LinkedIn profile activity data"""
        try:
            urls = ",".join(linkedin_urls)
            response = requests.get(
                f"{self.BASE_URL}/profile/{urls}/activity",
                headers=self.headers,
                params={"type": "posts"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def get_company_data(self, company_urls: List[str]) -> Dict:
        """Fetch LinkedIn company data"""
        try:
            urls = ",".join(company_urls)
            response = requests.get(
                f"{self.BASE_URL}/company/{urls}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
