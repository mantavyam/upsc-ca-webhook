# upsc-ca-webhook
A Python based webpage scraper which notifies a Discord Server Channel on updates via webhook.

# UPSC CA Essentials Bot

## HTML Structure Analysis

### Actual HTML Structure from Your Document:

```html
<div class="wrapper">
  <div class="list-category daily-news-list">
    <article>
      <div class="row">
        <!-- LEFT COLUMN: Daily Current Affairs -->
        <div class="column two box-toggle">
          <div class="box-slide">
            <p class="subheading affairs bg-green">Daily Current Affairs</p>
            <div class="box-hide">
              <ul>
                <li><a href="...">11 December 2025</a></li>
                <li><a href="...">10 December 2025</a></li>
                <!-- More links -->
              </ul>
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN: Important Editorials -->
        <div class="column two box-toggle">
          <div class="box-slide">
            <p class="subheading editorials bg-purple">Important Editorials</p>
            <div class="box-hide">
              <ul>
                <li><a href="...">India's Push for a Fairer,...</a></li>
                <!-- More links -->
              </ul>
            </div>
          </div>
        </div>
      </div>
    </article>
  </div>
</div>
```

### Key Observations:

1. **News Section Structure:**
   - Parent: `<div class="list-category daily-news-list">`
   - The links are inside: `<p class="subheading affairs bg-green">` → sibling `<div class="box-hide">` → `<ul>` → `<li>` → `<a>`

2. **Editorial Section Structure:**
   - The editorial section is NOT a sibling of news at the top level
   - It's a sibling at the `<div class="column two box-toggle">` level
   - Both columns are inside the same `<div class="row">`

## Setup Instructions

### 1. Create GitHub Repository

```bash
# On your local machine
mkdir drishti-monitor
cd drishti-monitor
git init

# Create files (copy code above)
# - drishti_bot.py
# - requirements.txt
# - .github/workflows/daily_check.yml

git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/drishti-monitor.git
git push -u origin main
```

### 2. Configure Discord Webhook

1. Open Discord → Your Server
2. Right-click the channel → **Edit Channel**
3. Go to **Integrations** → **Webhooks**
4. Click **Create Webhook**
5. Name it "Drishti Updates"
6. **Copy the Webhook URL**

### 3. Add Secret to GitHub

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `DISCORD_WEBHOOK`
4. Value: Paste your webhook URL
5. Click **Add secret**

### 4. Test the Bot

Go to **Actions** tab → Select "Drishti IAS Monitor" → Click **Run workflow**

Watch the logs to ensure it works correctly.

---

## Key Improvements Over Original Code

| Feature | Original | Corrected |
|---------|----------|-----------|
| **Editorial Parsing** | Uses `find_next()` (unreliable) | Uses parent navigation (precise) |
| **Link Extraction** | Gets all `<a>` tags | Targets only `<ul>` list items |
| **Error Handling** | Minimal | Comprehensive try-catch blocks |
| **History Size** | 10 items | 50 items (more robust) |
| **Discord Format** | Basic | Rich embeds with colors & timestamps |
| **Logging** | Basic prints | Detailed status indicators |
| **Commit Logic** | May fail on no changes | Handles empty commits gracefully |

---

## Monitoring & Maintenance

### Check Bot Status
- Go to **Actions** tab on GitHub
- View run history and logs
- Green checkmark = successful run
- Red X = error (click to see logs)

### Common Issues

**Issue:** Bot runs but no notifications
- **Check:** History file - may have already notified
- **Solution:** Manually delete `history.json` from repo

**Issue:** Parsing errors
- **Cause:** Website HTML changed
- **Solution:** Update selectors in `parse_news_section()` and `parse_editorial_section()`

**Issue:** Rate limiting from website
- **Cause:** Too many requests
- **Solution:** Reduce cron frequency

---

## Alternative: Run Locally

If you prefer running on your own computer:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DISCORD_WEBHOOK="your_webhook_url_here"

# Run manually
python drishti_bot.py

# Or schedule with cron (Linux/Mac)
crontab -e
# Add: 0 */2 * * * cd /path/to/drishti-monitor && python drishti_bot.py
```
