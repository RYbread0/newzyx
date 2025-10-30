import mimetypes
from pathlib import Path
import config
import helper

# ==================== STEP 3: CREATE PODCAST SCRIPT ====================
def create_podcast_script(summary_filename):
    """Convert summaries into podcast script"""
    print(f"🎙️ Step 3: Creating podcast script...")

    with open(summary_filename, "r", encoding="utf-8") as f:
        summaries = f.read()

    script_prompt = f"""You are creating a 3-minute podcast script for kids ages 10-16.

Take these 5 news summaries and turn them into a natural, conversational podcast script.

CRITICAL - Optimize for ages 10-16:
- Talk TO them, not DOWN to them - they're smart and curious
- Use a friendly, energetic tone like an older sibling or cool teacher
- Reference things they care about: school, friends, games, social media, their future
- Use casual language but not cringey ("literally," "honestly," natural speech patterns)
- Ask rhetorical questions to keep them engaged
- Connect news to their lives ("imagine if..." "this could affect your...")
- Use humor where appropriate but stay respectful of serious topics
- Include surprising facts that make them say "whoa, really?"
- Vary your sentence length - mix short punchy statements with longer explanations
- Use sound effects in words ("boom," "suddenly," "plot twist")
- Make transitions smooth and conversational, not robotic

Requirements:
- Start with an attention-grabbing hook (don't just say "hi, here's the news")
- Group related stories together naturally
- Use transitions that sound like real conversation
- End with something inspiring or thought-provoking, not just "bye"
- Exactly 3 minutes when read aloud (about 450-480 words)
- Reading level: 7th-8th grade
- Sound like a real podcast host having a conversation, not reading a script

Here are the summaries:

{summaries}

Write the complete podcast script now:"""

    response = config.openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system",
             "content": "You are an engaging podcast host for kids aged 10-16. You're enthusiastic, relatable, and treat your audience as intelligent people who deserve real news delivered in an exciting way. Think: charismatic teacher meets YouTube personality - informative but fun."},
            {"role": "user", "content": script_prompt}
        ]
    )

    script = response.choices[0].message.content.strip()

    date_str = helper.get_current_date_filename()
    script_filename = f"{date_str}_podcast_script.txt"

    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(script)

    print(f"✅ Saved podcast script to {script_filename}")
    return script_filename


# ==================== STEP 4: TEXT TO SPEECH ====================
def create_podcast_audio(script_filename):
    """Convert script to MP3 using OpenAI TTS"""
    print(f"🎵 Step 4: Creating podcast audio...")

    with open(script_filename, "r", encoding="utf-8") as f:
        script = f.read()

    response = config.openai_client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="sage",
        input=script,
        response_format="mp3"
    )

    date_str = helper.get_current_date_filename()
    audio_filename = f"{date_str}_podcast.mp3"

    with open(audio_filename, "wb") as f:
        f.write(response.read())

    print(f"✅ Saved podcast audio to {audio_filename}")
    return audio_filename


# ==================== STEP 5: UPLOAD TO S3 ====================
def upload_to_s3(summary_filename, audio_filename):
    """Upload summary and podcast to S3 with proper public access"""
    print(f"☁️ Step 5: Uploading to S3...")

    files_to_upload = [summary_filename, audio_filename]

    for filepath in files_to_upload:
        path = Path(filepath)

        # Determine content type
        content_type, _ = mimetypes.guess_type(str(path))
        if path.suffix == '.txt':
            content_type = 'text/plain; charset=utf-8'
        elif path.suffix == '.mp3':
            content_type = 'audio/mpeg'

        # Upload with public-read ACL and proper headers
        extra_args = {
            "ACL": "public-read",
            "ContentType": content_type,
            "CacheControl": "max-age=300"  # 5 minutes cache
        }

        # Upload using the filename as the S3 key (e.g., "10.29.25_news_summary.txt")
        s3_key = path.name
        config.s3_client.upload_file(str(path), config.S3_BUCKET, s3_key, ExtraArgs=extra_args)

        # Construct the public URL
        public_url = f"https://{config.S3_BUCKET}.s3.us-east-1.amazonaws.com/{s3_key}"
        print(f"  ✅ Uploaded: {public_url}")

    print(f"✅ All files uploaded successfully!")
    print(f"\n📍 Access your files at:")
    print(f"   Summary: https://{config.S3_BUCKET}.s3.us-east-1.amazonaws.com/{Path(summary_filename).name}")
    print(f"   Podcast: https://{config.S3_BUCKET}.s3.us-east-1.amazonaws.com/{Path(audio_filename).name}")
