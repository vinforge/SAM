#!/usr/bin/env python3
"""
Simple RSS feed test to debug the content extraction issue.
"""

import requests
import xml.etree.ElementTree as ET
import html

def test_rss_feed(url):
    """Test RSS feed parsing."""
    print(f"Testing RSS feed: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml'
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        print(f"Content type: {response.headers.get('content-type', 'Unknown')}")
        
        # Parse RSS XML
        content = response.content.decode('utf-8', errors='ignore')
        root = ET.fromstring(content)
        
        print(f"Root tag: {root.tag}")
        
        # Find items
        items = (root.findall('.//item') or 
                root.findall('.//{http://www.w3.org/2005/Atom}entry') or
                root.findall('.//entry'))
        
        print(f"Found {len(items)} items")
        
        # Test first few items
        for i, item in enumerate(items[:3]):
            print(f"\n--- Item {i} ---")
            
            # Print all child elements
            for child in item:
                print(f"  {child.tag}: {child.text[:100] if child.text else 'None'}...")
            
            # Extract title
            title_elem = (item.find('title') or 
                         item.find('.//{http://www.w3.org/2005/Atom}title'))
            title = ''
            if title_elem is not None:
                title = html.unescape(title_elem.text or '').strip()
            
            # Extract description
            desc_elem = (item.find('description') or 
                       item.find('summary') or 
                       item.find('.//{http://www.w3.org/2005/Atom}summary') or
                       item.find('.//{http://www.w3.org/2005/Atom}content'))
            description = ''
            if desc_elem is not None:
                description = html.unescape(desc_elem.text or '').strip()
            
            print(f"  Extracted title: '{title}'")
            print(f"  Extracted description: '{description[:100]}...'")
            print(f"  Title length: {len(title)}")
            print(f"  Description length: {len(description)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test different RSS feeds
    feeds = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "http://rss.cnn.com/rss/cnn_latest.rss"
    ]
    
    for feed in feeds:
        test_rss_feed(feed)
        print("\n" + "="*80 + "\n")
