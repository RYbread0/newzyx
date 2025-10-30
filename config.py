from openai import OpenAI
import boto3

S3_BUCKET = ""
NEWS_API_KEY = ""
OPENAI_API_KEY = ""
aws_access_key_id = ""
aws_secret_access_key = ""

# ==================== CONFIGURATION ====================

# Age group optimization settings
TARGET_AGE_MIN = 10
TARGET_AGE_MAX = 16
READING_LEVEL = "7th-8th grade"  # Appropriate for ages 10-16

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="us-east-1"
)
