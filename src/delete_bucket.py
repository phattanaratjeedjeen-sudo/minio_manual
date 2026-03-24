"""
Delete a bucket from MinIO (removes all objects first, then deletes the bucket)
"""

import os
import urllib3
from minio import Minio
from minio.error import S3Error

# ==================== Configuration ====================
minio_endpoint = "192.168.1.153:9000" 
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "encrypted-bucket" 

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

print("✓ Connected to MinIO")

try:
    if not minio_client.bucket_exists(bucket_name):
        print(f"✗ Bucket does not exist: {bucket_name}")
        raise SystemExit(0)

    print(f"Deleting bucket: {bucket_name}")
    
    # Remove all objects in the bucket first
    deleted_count = 0
    for obj in minio_client.list_objects(bucket_name, recursive=True, include_version=True):
        minio_client.remove_object(bucket_name, obj.object_name, version_id=obj.version_id)
        deleted_count += 1
    
    print(f"  - Removed {deleted_count} object(s)/version(s)")

    # Delete the empty bucket
    minio_client.remove_bucket(bucket_name)
    print(f"✓ Bucket deleted successfully: {bucket_name}")
    
except S3Error as err:
    print(f"✗ Delete bucket failed: {err}")
    raise