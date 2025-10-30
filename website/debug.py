import boto3
import requests
from datetime import datetime

# Your S3 configuration
S3_BUCKET = "kidsnewsfeed"
s3_client = boto3.client(
    "s3",
    aws_access_key_id="AKIA6AYRZ45KKZCZ23FF",
    aws_secret_access_key="z7TZIsbDZ20kTptSHCLdtYx3sMbzP5WKAUCqMdsq",
    region_name="us-east-1"
)

def get_current_date_filename():
    """Returns current date in M.D.YY format"""
    today = datetime.now()
    return f"{today.month}.{today.day}.{str(today.year % 100).zfill(2)}"

def test_s3_files():
    """Test if your S3 files are accessible"""
    print("=" * 60)
    print("S3 FILE ACCESSIBILITY TEST")
    print("=" * 60)
    print()
    
    date_str = get_current_date_filename()
    print(f"📅 Testing files for date: {date_str}")
    print()
    
    # File names to test
    summary_file = f"{date_str}_news_summary.txt"
    podcast_file = f"{date_str}_podcast.mp3"
    
    # Test 1: Check if files exist in S3
    print("TEST 1: Checking if files exist in S3...")
    print("-" * 60)
    
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
            print(f"✅ Found {len(files)} files in bucket:")
            for f in files:
                print(f"   - {f}")
            print()
            
            # Check if our specific files exist
            if summary_file in files:
                print(f"✅ Summary file EXISTS: {summary_file}")
            else:
                print(f"❌ Summary file NOT FOUND: {summary_file}")
                
            if podcast_file in files:
                print(f"✅ Podcast file EXISTS: {podcast_file}")
            else:
                print(f"❌ Podcast file NOT FOUND: {podcast_file}")
        else:
            print("❌ No files found in bucket!")
            
    except Exception as e:
        print(f"❌ Error listing bucket: {e}")
    
    print()
    print("TEST 2: Checking file permissions (ACL)...")
    print("-" * 60)
    
    for filename in [summary_file, podcast_file]:
        try:
            acl = s3_client.get_object_acl(Bucket=S3_BUCKET, Key=filename)
            is_public = any(
                grant.get('Permission') == 'READ' and 
                grant.get('Grantee', {}).get('Type') == 'Group' and
                'AllUsers' in grant.get('Grantee', {}).get('URI', '')
                for grant in acl.get('Grants', [])
            )
            
            if is_public:
                print(f"✅ {filename} is PUBLIC")
            else:
                print(f"❌ {filename} is NOT PUBLIC")
                print(f"   Grants: {acl.get('Grants')}")
                
        except Exception as e:
            print(f"❌ Error checking {filename}: {e}")
    
    print()
    print("TEST 3: Testing public URLs...")
    print("-" * 60)
    
    base_url = f"https://{S3_BUCKET}.s3.us-east-1.amazonaws.com"
    
    for filename in [summary_file, podcast_file]:
        url = f"{base_url}/{filename}"
        print(f"Testing: {url}")
        
        try:
            response = requests.head(url, timeout=10)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ ACCESSIBLE!")
                print(f"   Content-Type: {response.headers.get('Content-Type')}")
                print(f"   Content-Length: {response.headers.get('Content-Length')} bytes")
            elif response.status_code == 403:
                print(f"   ❌ FORBIDDEN - File is not public!")
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND - File doesn't exist!")
            else:
                print(f"   ❌ ERROR")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("TEST 4: Check CORS configuration...")
    print("-" * 60)
    
    try:
        cors = s3_client.get_bucket_cors(Bucket=S3_BUCKET)
        print("✅ CORS is configured:")
        for i, rule in enumerate(cors.get('CORSRules', []), 1):
            print(f"\n   Rule {i}:")
            print(f"   - Allowed Methods: {rule.get('AllowedMethods')}")
            print(f"   - Allowed Origins: {rule.get('AllowedOrigins')}")
            print(f"   - Allowed Headers: {rule.get('AllowedHeaders')}")
    except Exception as e:
        if 'NoSuchCORSConfiguration' in str(e):
            print("❌ CORS is NOT configured!")
            print("\nTo fix, run this in your Python script:")
            print("""
cors_config = {
    'CORSRules': [{
        'AllowedHeaders': ['*'],
        'AllowedMethods': ['GET', 'HEAD'],
        'AllowedOrigins': ['*'],
        'ExposeHeaders': ['ETag', 'Last-Modified'],
        'MaxAgeSeconds': 3600
    }]
}
s3_client.put_bucket_cors(Bucket='kidsnewsfeed', CORSConfiguration=cors_config)
            """)
        else:
            print(f"❌ Error checking CORS: {e}")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nYour files should be at:")
    print(f"📄 {base_url}/{summary_file}")
    print(f"🎵 {base_url}/{podcast_file}")
    print()

if __name__ == "__main__":
    test_s3_files()