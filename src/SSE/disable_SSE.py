from minio import Minio
from minio.sseconfig import SSEConfig, Rule
import urllib3
import os

# ==================== Configuration ====================
minio_endpoint = "192.168.1.153:9000"   
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "buck1"                


# CA certificate configuration
minio_ca_cert = os.path.expanduser("~/asus-public.crt") 
print(f"Using CA certificate: {minio_ca_cert}")   


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
    # You don't need to create a 'config' or 'Rule' object to disable it.
    # Just call the delete method on the bucket name.
    minio_client.delete_bucket_encryption(bucket_name=bucket_name)
    
    print("SSE-KMS encryption has been DISABLED successfully.")
    print(f"New files uploaded to '{bucket_name}' will now be plaintext.")

except Exception as e:
    print(f"Failed to disable encryption: {e}")
