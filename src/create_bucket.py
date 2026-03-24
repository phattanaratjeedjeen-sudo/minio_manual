"""
Create a bucket in MinIO
"""

import os
import urllib3
from minio import Minio

# ==================== Configuration ====================
minio_endpoint = "192.168.1.153:9000" 
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "my-bucket" 

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

# Create bucket
try:
    if minio_client.bucket_exists(bucket_name):
        print(f"✓ Bucket '{bucket_name}' already exists")
    else:
        minio_client.make_bucket(bucket_name)
        print(f"✓ Bucket '{bucket_name}' created successfully")
except Exception as err:
    print(f"✗ Error: {err}")
    raise
