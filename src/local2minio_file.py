"""
Upload a file to MinIO bucket
"""

import os
import urllib3
from minio import Minio


# ==================== Configuration ====================
minio_endpoint = "192.168.1.152:9000" 
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "my-bucket"

# Local file to upload
filename = "SSE_key.txt"
local_file_path = os.path.expanduser(f"~/{filename}")  
object_name = filename    

# CA certificate configuration
minio_ca_cert = os.path.expanduser("~/minio/certs/public.crt")    


if not os.path.isfile(minio_ca_cert):
    raise SystemExit(f"CA certificate not found: {minio_ca_cert}")

if not os.path.isfile(local_file_path):
    raise SystemExit(f"Local file not found: {local_file_path}")

print(f"Using CA cert: {minio_ca_cert}")
print(f"Uploading file: {local_file_path}")

# Create HTTP client with custom CA certificate
http_client = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=minio_ca_cert,
)

# Initialize MinIO client
minio_client = Minio(
    minio_endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=True,
    cert_check=True,
    http_client=http_client,
)

# Upload file
try:
    file_size = os.path.getsize(local_file_path)
    
    result = minio_client.fput_object(
        bucket_name,
        object_name,
        local_file_path,
    )
    
    print(f"✓ File uploaded successfully")
    print(f"  - Bucket: {bucket_name}")
    print(f"  - Object: {object_name}")
    print(f"  - Size: {file_size} bytes")
    print(f"  - ETag: {result.etag}")
    
except Exception as err:
    print(f"✗ Error uploading file: {err}")
    raise


