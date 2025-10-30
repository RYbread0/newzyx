import config
import fetch
import script
import selectsum

# ==================== S3 CORS CONFIGURATION ====================
def setup_s3_cors():
    """Configure CORS for S3 bucket (run once)"""
    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'HEAD'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': ['ETag', 'Last-Modified'],
            'MaxAgeSeconds': 3600
        }]
    }

    try:
        config.s3_client.put_bucket_cors(
            Bucket=config.S3_BUCKET,
            CORSConfiguration=cors_configuration
        )
        print(f"✅ CORS configured for bucket: {config.S3_BUCKET}")
    except Exception as e:
        print(f"❌ Error setting CORS: {e}")


# ==================== MAIN EXECUTION ====================
def main():
    """Run the complete pipeline"""
    print("=" * 60)
    print("KIDS NEWS PIPELINE - AUTOMATED DAILY NEWS")
    print("=" * 60)
    print()

    # OPTIONAL: Uncomment this line to set up CORS (only needs to run once)
    # setup_s3_cors()

    # Topics to fetch
    topics = [
        "technology", "sports", "finance", "politics", "health",
        "science", "travel", "education", "environment", "entertainment"
    ]

    try:
        # Step 1: Fetch 21 headlines
        csv_file = fetch.fetch_headlines(topics, articles_per_topic=3, max_total=21)
        print()

        # Step 2: Select best 5 and summarize
        summary_file = selectsum.select_and_summarize(csv_file)
        print()

        # Step 3: Create podcast script
        script_file = script.create_podcast_script(summary_file)
        print()

        # Step 4: Create audio
        audio_file = script.create_podcast_audio(script_file)
        print()

        # Step 5: Upload to S3
        script.upload_to_s3(summary_file, audio_file)
        print()

        print("=" * 60)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 60)
        print(f"📄 Summary: {summary_file}")
        print(f"🎵 Podcast: {audio_file}")
        print(f"☁️ Both uploaded to S3 bucket: {config.S3_BUCKET}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# ==================== END OF CODE ====================