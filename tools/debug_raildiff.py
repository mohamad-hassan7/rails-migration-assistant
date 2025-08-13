#!/usr/bin/env python3
"""
debug_raildiff.py - Debug railsdiff.org structure
"""
import requests
from bs4 import BeautifulSoup

def debug_raildiff_page():
    url = "https://railsdiff.org/4.2.11/5.0.0"
    print(f"Fetching: {url}")
    
    try:
        resp = requests.get(url, timeout=30)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"Failed to fetch page")
            return
            
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for various diff-related elements
        selectors = [
            ".diff-file-wrapper",
            ".diff-file",  
            ".file-diff",
            "[class*='diff']",
            ".file",
            ".change"
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            print(f"{selector}: {len(elements)} elements")
        
        # Print first 2000 chars of HTML to see structure
        print("\n--- HTML SAMPLE ---")
        print(resp.text[:2000])
        print("--- END SAMPLE ---")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_raildiff_page()
