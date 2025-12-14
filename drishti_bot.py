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
    # color = 3066993 if category == "Daily Current Affairs" else 10181046
    color = 3447003 if category == "Daily Current Affairs" else 15158332
    
    embed = {
        "username": "Drill Ustaad - IMA",
        "avatar_url": "https://i.ibb.co/Q79mP6CC/ima-ustad.jpg",
        "embeds": [{
            "title": f"{title}",
            "description": (
                f"New update available in {category} section!\n"
                f"[Click to Read full article]({link})"
            ),
            "url": link,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Exam Oriented • Daily Updates to Prepare thyself for the Written and SSB of the upcoming UPSC CDS Exam"
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
                data = json.load(f)
                # Ensure news_articles key exists for backward compatibility
                if "news_articles" not in data:
                    data["news_articles"] = []
                return data
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
            return {"news": [], "editorials": [], "news_articles": []}
    return {"news": [], "editorials": [], "news_articles": []}

def save_history(history):
    """Save notified URLs to history file."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"✓ History saved ({len(history['news'])} news, {len(history['editorials'])} editorials, {len(history.get('news_articles', []))} articles)")
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

def fetch_news_of_the_day(date_url):
    """Fetch 'News of the Day' articles from a specific date's page."""
    articles = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"  ⟳ Fetching News of the Day from: {date_url}")
        response = requests.get(date_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the "News of the day" section
        # Based on HTML: <div class="category news"> with <p class="subheading bg-yellow">News of the day</p>
        news_category = soup.find("div", class_="category news")
        
        if not news_category:
            print("  ⚠ News of the day section not found")
            return articles
        
        # Get the <ul> containing the article links
        ul = news_category.find("ul")
        if not ul:
            print("  ⚠ News articles <ul> not found")
            return articles
        
        # Extract all article links
        for li in ul.find_all("li"):
            a_tag = li.find("a", href=True)
            if a_tag:
                # Extract the article title and full URL
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href")
                
                # The href contains anchor links like #33225, need to build full URL
                # Format: base_url + href (href already includes the date and anchor)
                full_url = href if href.startswith("http") else f"https://www.drishtiias.com{href}"
                
                articles.append({
                    "title": title,
                    "url": full_url
                })
        
        print(f"  ✓ Found {len(articles)} news articles")
        
    except Exception as e:
        print(f"  ✗ Error fetching news of the day: {e}")
    
    return articles

def send_news_of_the_day_notification(date_title, articles, date_url):
    """Send a consolidated notification with all News of the Day articles."""
    if not DISCORD_WEBHOOK or not articles:
        return False
    
    # Build the description with all articles as a numbered list
    description = f"**{len(articles)} articles published on {date_title}:**\n\n"
    
    for idx, article in enumerate(articles, 1):
        # Create clickable links in Discord markdown format
        description += f"{idx}. [{article['title']}]({article['url']})\n"
    
    # Add a footer link to the main date page
    description += f"\n[View full page]({date_url})"
    
    embed = {
        "username": "Drill Ustaad - IMA",
        "avatar_url": "https://i.ibb.co/Q79mP6CC/ima-ustad.jpg",
        "embeds": [{
            "title": "News of the Day",
            "description": description,
            "url": date_url,
            "color": 3447003,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Exam Oriented • Daily Updates to Prepare thyself for the Written and SSB of the upcoming UPSC CDS Exam"
            }
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=embed, timeout=10)
        response.raise_for_status()
        print(f"✓ Sent News of the Day notification ({len(articles)} articles)")
        return True
    except Exception as e:
        print(f"✗ Failed to send News of the Day notification: {e}")
        return False

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
    news_date_to_fetch = None  # Track if we need to fetch News of the Day
    
    for link_data in reversed(news_links[:5]):  # Check top 5 most recent
        url = link_data["url"]
        title = link_data["title"]
        
        if url not in history["news"]:
            if send_discord_notification(title, url, "Daily Current Affairs"):
                history["news"].append(url)
                history["news"] = history["news"][-MAX_HISTORY_SIZE:]
                new_items_found = True
                
                # Mark that we need to fetch News of the Day for this date
                if not news_date_to_fetch:
                    news_date_to_fetch = {
                        "url": url,
                        "title": title
                    }
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
    
    # NEW FEATURE: Fetch and send "News of the Day" articles if there's a new update
    if news_date_to_fetch:
        print("\n--- Fetching News of the Day ---")
        date_url = news_date_to_fetch["url"]
        date_title = news_date_to_fetch["title"]
        
        # Check if we've already sent news articles for this date
        if date_url not in history.get("news_articles", []):
            articles = fetch_news_of_the_day(date_url)
            
            if articles:
                if send_news_of_the_day_notification(date_title, articles, date_url):
                    # Add to history to prevent duplicate notifications
                    if "news_articles" not in history:
                        history["news_articles"] = []
                    history["news_articles"].append(date_url)
                    history["news_articles"] = history["news_articles"][-MAX_HISTORY_SIZE:]
                    new_items_found = True
        else:
            print(f"⊘ Already sent News of the Day for: {date_title}")
    
    # Save updated history
    if new_items_found:
        save_history(history)
        print("\n✓ New updates sent to Discord!")
    else:
        print("\n⊘ No new updates found")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
