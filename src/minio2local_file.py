import os
import urllib3
from minio import Minio
from minio.error import S3Error

# ==================== Configuration ====================
minio_endpoint = "192.168.1.152:9000"   
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "my-bucket"  
object_name = "ip_note.txt"
local_path = os.path.expanduser("~")          


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


download_path = os.path.join(local_path, object_name)
try:
    minio_client.fget_object(bucket_name, object_name, download_path)
    print(f"✓ Downloaded: {object_name} → {download_path}")
except S3Error as e:
    print(f"✗ Error: {e}")