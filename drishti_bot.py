import requests
from bs4 import BeautifulSoup
import json
import os
import sys
from datetime import datetime

# --- CONFIGURATION ---
URL = "https://www.drishtiias.com/current-affairs-news-analysis-editorials"
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
HISTORY_FILE = "history.json"
MAX_HISTORY_SIZE = 50  # Keep more history to be safe

def send_discord_notification(title, link, category):
    """Sends a formatted embed to Discord."""
    if not DISCORD_WEBHOOK:
        print("ERROR: DISCORD_WEBHOOK environment variable not set!")
        return False
    
    # Clean up title (remove ellipsis, extra spaces)
    title = title.strip().replace("...", "")
    
    # Color coding: Green for News, Purple for Editorials
    color = 3066993 if category == "Daily Current Affairs" else 10181046
    
    embed = {
        "username": "Essentials",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",  # Optional: Add icon
        "embeds": [{
            "title": f"🆕 New {category}",
            "description": f"**{title}**",
            "url": link,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Exam Oriented • Daily Updates"
            }
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=embed, timeout=10)
        response.raise_for_status()
        print(f"✓ Sent: {category} - {title[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to send notification: {e}")
        return False

def load_history():
    """Load previously notified URLs from history file."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
            return {"news": [], "editorials": []}
    return {"news": [], "editorials": []}

def save_history(history):
    """Save notified URLs to history file."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"✓ History saved ({len(history['news'])} news, {len(history['editorials'])} editorials)")
    except Exception as e:
        print(f"✗ Error saving history: {e}")

def parse_news_section(soup):
    """Parse Daily Current Affairs section."""
    links = []
    try:
        # Find the news section by class
        news_section = soup.find("div", class_="daily-news-list")
        if not news_section:
            print("⚠ News section not found")
            return links
        
        # Navigate to the box-hide div containing the list
        box_hide = news_section.find("div", class_="box-hide")
        if not box_hide:
            print("⚠ News box-hide not found")
            return links
        
        # Get the <ul> containing links
        ul = box_hide.find("ul")
        if not ul:
            print("⚠ News <ul> not found")
            return links
        
        # Get all <a> tags in list items
        for li in ul.find_all("li"):
            a_tag = li.find("a", href=True)
            if a_tag:
                links.append({
                    "title": a_tag.get_text(strip=True),
                    "url": a_tag["href"]
                })
        
        print(f"✓ Found {len(links)} news links")
        
    except Exception as e:
        print(f"✗ Error parsing news section: {e}")
    
    return links

def parse_editorial_section(soup):
    """Parse Important Editorials section."""
    links = []
    try:
        # Find the editorials header
        editorial_header = soup.find("p", class_="editorials")
        if not editorial_header:
            print("⚠ Editorial header not found")
            return links
        
        # Get the parent box-slide, then find box-hide within it
        box_slide = editorial_header.parent
        box_hide = box_slide.find("div", class_="box-hide")
        
        if not box_hide:
            print("⚠ Editorial box-hide not found")
            return links
        
        # Get the <ul> containing links
        ul = box_hide.find("ul")
        if not ul:
            print("⚠ Editorial <ul> not found")
            return links
        
        # Get all <a> tags in list items
        for li in ul.find_all("li"):
            a_tag = li.find("a", href=True)
            if a_tag:
                links.append({
                    "title": a_tag.get_text(strip=True),
                    "url": a_tag["href"]
                })
        
        print(f"✓ Found {len(links)} editorial links")
        
    except Exception as e:
        print(f"✗ Error parsing editorial section: {e}")
    
    return links

def main():
    print("=" * 60)
    print(f"Drishti IAS Bot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Validate webhook
    if not DISCORD_WEBHOOK:
        print("✗ DISCORD_WEBHOOK not configured!")
        sys.exit(1)
    
    # Fetch the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"⟳ Fetching {URL}...")
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"✓ Page fetched ({len(response.text)} bytes)")
    except Exception as e:
        print(f"✗ Failed to fetch page: {e}")
        sys.exit(1)
    
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    history = load_history()
    new_items_found = False
    
    # Parse both sections
    news_links = parse_news_section(soup)
    editorial_links = parse_editorial_section(soup)
    
    # Process news (most recent first, but notify oldest to newest)
    print("\n--- Processing News ---")
    for link_data in reversed(news_links[:5]):  # Check top 5 most recent
        url = link_data["url"]
        title = link_data["title"]
        
        if url not in history["news"]:
            if send_discord_notification(title, url, "Daily Current Affairs"):
                history["news"].append(url)
                history["news"] = history["news"][-MAX_HISTORY_SIZE:]
                new_items_found = True
        else:
            print(f"⊘ Already notified: {title[:50]}...")
    
    # Process editorials (most recent first, but notify oldest to newest)
    print("\n--- Processing Editorials ---")
    for link_data in reversed(editorial_links[:5]):  # Check top 5 most recent
        url = link_data["url"]
        title = link_data["title"]
        
        if url not in history["editorials"]:
            if send_discord_notification(title, url, "Important Editorial"):
                history["editorials"].append(url)
                history["editorials"] = history["editorials"][-MAX_HISTORY_SIZE:]
                new_items_found = True
        else:
            print(f"⊘ Already notified: {title[:50]}...")
    
    # Save updated history
    if new_items_found:
        save_history(history)
        print("\n✓ New updates sent to Discord!")
    else:
        print("\n⊘ No new updates found")
    
    print("=" * 60)

if __name__ == "__main__":
    main()