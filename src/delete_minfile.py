"""
Delete a file (object) from MinIO bucket
"""

import os
import urllib3
from minio import Minio
from minio.error import S3Error

# ==================== Configuration ====================
minio_endpoint = "192.168.1.153:9000"  
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "my-bucket"   
object_name = "SSE_key.txt"

# CA certificate configuration
minio_ca_cert = os.path.expanduser("~/minio/certs/public.crt")


if not os.path.isfile(minio_ca_cert):
    raise SystemExit(f"CA certificate not found: {minio_ca_cert}")


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


try:
    # Check if bucket exists
    if not minio_client.bucket_exists(bucket_name):
        print(f"✗ Bucket does not exist: {bucket_name}")
        raise SystemExit(1)
    
    print(f"Deleting file: {object_name}")
    
    # Delete the object
    minio_client.remove_object(bucket_name, object_name)
    
    print(f"✓ File deleted successfully")
    print(f"  - Bucket: {bucket_name}")
    print(f"  - File: {object_name}")
    
except S3Error as err:
    print(f"✗ Delete failed: {err}")
    raise

