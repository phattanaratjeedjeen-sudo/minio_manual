from minio import Minio
import urllib3
import os

myhp = "192.168.1.152:9000"

# Determine the CA certificate path of upstream MinIO server
minio_ca_cert = os.environ.get("MINIO_CA_CERT", "/home/wa/minio/certs/public.crt")

if not os.path.isfile(minio_ca_cert):
    raise SystemExit(f"CA certificate not found: {minio_ca_cert}")

print(f"Using CA cert: {minio_ca_cert}")

# Create HTTP client with custom CA certificate
http_client = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=minio_ca_cert,
)

minio_client = Minio(
    myhp,
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True,           # ✓ Uses HTTPS
    cert_check=True,       # ✓ Verifies certificate
    http_client=http_client,  # ✓ Uses custom CA cert
)

# Test connection by listing buckets
try:
    buckets = minio_client.list_buckets()
    print("✓ Connection successful!")
    print(f"✓ MinIO server: {myhp}")
    print(f"✓ Found {len(buckets)} bucket(s):")
    for bucket in buckets:
        print(f"  - {bucket.name} (created: {bucket.creation_date})")
except Exception as err:
    print(f"✗ Connection failed: {err}")
    raise

