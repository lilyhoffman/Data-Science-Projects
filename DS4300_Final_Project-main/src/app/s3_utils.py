import os
import json
import boto3
from dotenv import load_dotenv
from datetime import datetime

# Load .env variables
load_dotenv()

AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

# Create S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    region_name=AWS_REGION
)

def upload_user_data_to_s3(user_data, identifier):
    """
    Uploads a dictionary as a JSON file to S3.

    Args:
        user_data (dict): Dictionary of user inputs.
        identifier (str): A string to uniquely identify the file (e.g., email or userID).
    """
    try:
        #timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_name = f"user_uploads/{identifier}"

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=file_name,
            Body=json.dumps(user_data),
            ContentType="application/json"
        )

        return file_name
    except Exception as e:
        raise RuntimeError(f"S3 Upload failed: {e}")
