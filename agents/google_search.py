"""
Google Search Integration for Jarvis v2
Uses Google Custom Search JSON API for high-quality web search.

API Key: Stored in config
Quota: 100 free queries/day, $5 per 1000 after
"""
import os
import requests
from typing import List, Dict, Optional
from datetime import datetime
from .config import WORKSPACE_DIR

# Google Custom Search API configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyB25xk-Gy3SzriHeV0BEHE0IVaYoHziKko")
# You need to create a Programmable Search Engine at https://programmablesearchengine.google.com/
# Set it to search the entire web, then get the Search Engine ID (cx)
GOOGLE_CX = os.environ.get("GOOGLE_CX", "")  # User needs to set this


class GoogleSearchAgent:
    """
    Google Custom Search integration for Jarvis.
    
    Features:
    - Full Google Search index access
    - Image search support
    - Site-restricted search
    - Date filtering
    - Safe search control
    """
    
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.cx = GOOGLE_CX
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.daily_quota = 100
        self.queries_today = 0
        self.last_reset = datetime.now().date()
        
        if not self.cx:
            print("[GoogleSearch] Warning: GOOGLE_CX not set. Create a Programmable Search Engine first.")
    
    def _check_quota(self) -> bool:
        """Check if we have queries remaining."""
        today = datetime.now().date()
        if today != self.last_reset:
            self.queries_today = 0
            self.last_reset = today
        
        if self.queries_today >= self.daily_quota:
            print(f"[GoogleSearch] Daily quota exhausted ({self.daily_quota} queries)")
            return False
        return True
    
    def search(self, query: str, num_results: int = 10, 
               site: str = None, date_restrict: str = None,
               search_type: str = None) -> List[Dict]:
        """
        Perform a Google search.
        
        Args:
            query: Search query
            num_results: Number of results (1-10 per request, max 100 total)
            site: Restrict to specific site (e.g., "reddit.com")
            date_restrict: Date restriction (d1=past day, w1=past week, m1=past month, y1=past year)
            search_type: "image" for image search, None for web search
        
        Returns:
            List of search results with title, link, snippet
        """
        if not self._check_quota():
            return []
        
        if not self.cx:
            print("[GoogleSearch] Error: Search Engine ID (cx) not configured")
            return []
        
        # Build search query
        if site:
            query = f"site:{site} {query}"
        
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": min(num_results, 10),  # API max is 10 per request
        }
        
        if date_restrict:
            params["dateRestrict"] = date_restrict
        
        if search_type == "image":
            params["searchType"] = "image"
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            self.queries_today += 1
            
            if response.status_code != 200:
                print(f"[GoogleSearch] API error: {response.status_code}")
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                result = {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "google",
                }
                
                # Add image-specific fields
                if search_type == "image":
                    result["image"] = item.get("link", "")
                    result["thumbnail"] = item.get("image", {}).get("thumbnailLink", "")
                
                results.append(result)
            
            print(f"[GoogleSearch] Found {len(results)} results for: {query[:50]}...")
            return results
            
        except Exception as e:
            print(f"[GoogleSearch] Error: {e}")
            return []
    
    def search_news(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search recent news (past week)."""
        return self.search(query, num_results, date_restrict="w1")
    
    def search_reddit(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search Reddit via Google."""
        return self.search(query, num_results, site="reddit.com")
    
    def search_stackoverflow(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search StackOverflow via Google."""
        return self.search(query, num_results, site="stackoverflow.com")
    
    def search_github(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search GitHub via Google."""
        return self.search(query, num_results, site="github.com")
    
    def search_academic(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search academic sources via Google."""
        results = []
        # Search multiple academic sites
        for site in ["arxiv.org", "scholar.google.com", "researchgate.net"]:
            results.extend(self.search(query, num_results=3, site=site))
        return results[:num_results]
    
    def search_images(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search for images."""
        return self.search(query, num_results, search_type="image")
    
    def multi_search(self, query: str, categories: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Perform searches across multiple categories.
        
        Args:
            query: Search query
            categories: List of categories to search (default: all)
                       Options: web, news, reddit, stackoverflow, github, academic
        
        Returns:
            Dict mapping category to results
        """
        if categories is None:
            categories = ["web", "news", "reddit", "academic"]
        
        results = {}
        
        for category in categories:
            if category == "web":
                results["web"] = self.search(query, num_results=5)
            elif category == "news":
                results["news"] = self.search_news(query, num_results=5)
            elif category == "reddit":
                results["reddit"] = self.search_reddit(query, num_results=5)
            elif category == "stackoverflow":
                results["stackoverflow"] = self.search_stackoverflow(query, num_results=5)
            elif category == "github":
                results["github"] = self.search_github(query, num_results=5)
            elif category == "academic":
                results["academic"] = self.search_academic(query, num_results=5)
        
        return results
    
    def get_quota_status(self) -> Dict:
        """Get current quota status."""
        return {
            "daily_limit": self.daily_quota,
            "used_today": self.queries_today,
            "remaining": self.daily_quota - self.queries_today,
            "reset_date": str(self.last_reset)
        }


# Singleton instance
google_search = GoogleSearchAgent()
