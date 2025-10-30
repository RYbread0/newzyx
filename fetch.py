import requests
import csv
import time
import config
import helper


# ==================== STEP 1: FETCH 21 HEADLINES ====================
def fetch_headlines(topics, articles_per_topic=3, max_total=21):
    """Fetch unique headlines from NewsAPI and save to CSV"""
    print(f"📰 Step 1: Fetching {max_total} headlines...")

    rows = []
    for topic in topics:
        params = {
            "q": topic,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 100,
            "searchIn": "title",
            "apiKey": config.NEWS_API_KEY,
            "excludeDomains": ",".join(helper.DEFAULT_EXCLUDE_DOMAINS)
        }

        r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=20)
        data = r.json()

        if r.status_code != 200 or "articles" not in data:
            print(f"⚠️ Error fetching {topic}: {data.get('message', 'Unknown error')}")
            continue

        seen_urls = set()
        seen_bases = set()
        seen_sigs = set()
        count = 0

        for article in data["articles"]:
            if count >= articles_per_topic:
                break

            title = article.get("title") or ""
            url = article.get("url") or ""

            if not title or not url or helper._is_ad(title):
                continue

            # Deduplication checks
            kurl = helper._norm_url(url)
            if kurl in seen_urls:
                continue

            base = helper._base_title(title)
            if base in seen_bases:
                continue

            sig = helper._title_signature(title)
            if sig in seen_sigs:
                continue

            seen_urls.add(kurl)
            seen_bases.add(base)
            seen_sigs.add(sig)
            rows.append((topic, title, url))
            count += 1

        time.sleep(0.5)  # Rate limiting

    # Limit to max_total
    rows = rows[:max_total]

    # Save to CSV with date
    date_str = helper.get_current_date_filename()
    csv_filename = f"{date_str}_headlines.csv"

    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Topic", "Title", "URL"])
        writer.writerows(rows)

    print(f"✅ Saved {len(rows)} headlines to {csv_filename}")
    return csv_filename
