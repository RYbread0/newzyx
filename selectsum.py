import requests
import csv
from bs4 import BeautifulSoup
import time
import config
import helper

# ==================== STEP 2: SELECT BEST 5 & SUMMARIZE ====================
def select_and_summarize(csv_filename):
    """OpenAI selects best 5 articles and summarizes them"""
    print(f"🤖 Step 2: Selecting best 5 articles and summarizing...")

    # Read CSV
    with open(csv_filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        articles = [{"topic": row["Topic"], "title": row["Title"], "url": row["URL"]} for row in reader]

    # Create article list for OpenAI
    article_list = "\n\n".join([
        f"{i + 1}. [{article['topic'].upper()}] {article['title']}\nURL: {article['url']}"
        for i, article in enumerate(articles)
    ])

    # Ask OpenAI to select best 5
    selection_prompt = f"""You are a news editor for a kids' news website (ages 10-16).

Below are {len(articles)} news headlines. Your task:

1. Select the 5 BEST articles that would be most interesting, educational, and age-appropriate for kids
2. For each selected article, fetch and read the content from the URL
3. Write a clear, engaging summary of each article (4-6 bullet points per article)
4. Make summaries kid-friendly, educational, and appropriate for ages 10-16
5. Explain complex terms simply
6. Cover who/what/where/when/why/how

CRITICAL - EXCLUDE any articles about:
- Violence, murder, mass shootings, terrorism, war crimes
- Sexual content, abuse, assault, harassment
- Graphic accidents or deaths
- Drug overdoses or substance abuse details
- Suicide or self-harm
- Adult/mature themes not suitable for children
- Disturbing or traumatic events

PREFER articles about:
- Science discoveries and technology innovations
- Sports achievements and inspiring athletes
- Environmental progress and conservation
- Educational topics and learning
- Cultural events and entertainment (age-appropriate)
- Health and wellness (age-appropriate)
- Positive community stories and achievements

Format your response EXACTLY like this:
1. [TOPIC] Title
- bullet point 1
- bullet point 2
- bullet point 3
...

2. [TOPIC] Title
- bullet point 1
...

Here are the articles:

{article_list}"""

    # Fetch article content and summarize
    summaries = []
    selected_articles = []

    # First, let OpenAI choose the 5 best
    selection_response = config.openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": """You are an expert news editor for kids aged 10-16. 

Your PRIMARY responsibility is ensuring content is age-appropriate and safe. NEVER select articles about:
- Violence, murder, shootings, terrorism, war crimes
- Sexual content, abuse, assault, harassment  
- Graphic deaths or disturbing accidents
- Drug/substance abuse details
- Suicide or self-harm
- Adult/mature themes

Always prioritize positive, educational, and inspiring stories about science, technology, sports, environment, culture, and achievement."""},
            {"role": "user",
             "content": f"From these {len(articles)} articles, list ONLY the numbers (1-{len(articles)}) of the 5 BEST articles for kids aged 10-16, separated by commas. Exclude any inappropriate content:\n\n{article_list}"}
        ]
    )

    selected_nums = selection_response.choices[0].message.content.strip()
    print(f"📋 OpenAI selected articles: {selected_nums}")

    # Parse selected numbers
    try:
        indices = [int(n.strip()) - 1 for n in selected_nums.split(",")][:5]
        selected_articles = [articles[i] for i in indices if 0 <= i < len(articles)]
    except:
        # Fallback: take first 5
        selected_articles = articles[:5]

    # Now summarize each selected article
    for i, article in enumerate(selected_articles, 1):
        print(f"  Processing {i}/5: {article['title'][:60]}...")

        try:
            # Fetch article content
            headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsSummarizer/1.0)"}
            r = requests.get(article["url"], headers=headers, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            node = soup.find("article")
            paragraphs = node.find_all("p") if node else soup.find_all("p")
            article_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
            article_text = " ".join(article_text.split())[:7000]

            if len(article_text) < 300:
                article_text = f"Limited content available. Title: {article['title']}"

        except Exception as e:
            print(f"    ⚠️ Could not fetch article: {e}")
            article_text = f"Could not retrieve full article content. Title: {article['title']}"

        # Summarize with OpenAI
        summary_prompt = f"""Summarize this news article for kids ages 10-16.

Topic: {article['topic']}
Title: {article['title']}

Article:
{article_text}

IMPORTANT - Content Safety Check:
- If this article contains inappropriate content (violence, sexual content, abuse, graphic details, disturbing themes), respond with ONLY: "INAPPROPRIATE - SKIP"
- Otherwise, create the summary as instructed below.

Create 5-7 clear bullet points optimized for ages 10-16:
- Start with the main story in ONE sentence that hooks their attention
- Use active voice and vivid language that makes it real and interesting
- Connect to things kids care about (school, technology, environment, sports, their future)
- Explain complex terms in relatable ways (use analogies to things they know)
- Include surprising facts or "did you know" moments
- Show WHY this matters to THEM specifically
- Use conversational tone like you're explaining to a friend
- Avoid talking down - treat them as intelligent readers
- Keep sentences short and punchy (max 15-20 words per sentence)

Format as bullet points only (no numbering, just dashes)."""

        response = config.openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system",
                 "content": "You are a friendly news writer for kids aged 10-16. Make news clear, engaging, and educational. Write at a 7th-8th grade reading level with exciting language that respects their intelligence. ALWAYS check if content is age-appropriate first."},
                {"role": "user", "content": summary_prompt}
            ]
        )

        summary = response.choices[0].message.content.strip()

        # Skip if flagged as inappropriate
        if "INAPPROPRIATE" in summary.upper() and "SKIP" in summary.upper():
            print(f"    ⚠️ Skipped inappropriate content")
            continue

        summaries.append(f"{i}. [{article['topic'].upper()}] {article['title']}\n{summary}")
        time.sleep(1)  # Rate limiting

    # Check if we got enough summaries (need at least 3)
    if len(summaries) < 3:
        print(f"⚠️ Warning: Only got {len(summaries)} appropriate articles. Trying to find more...")
        # Could add logic here to fetch more articles if needed

    # Save summaries
    date_str = helper.get_current_date_filename()
    summary_filename = f"{date_str}_news_summary.txt"

    with open(summary_filename, "w", encoding="utf-8") as f:
        f.write("\n\n".join(summaries))

    print(f"✅ Saved summaries to {summary_filename}")
    return summary_filename

