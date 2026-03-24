"""
Check MinIO connection with TLS and SSE status
"""

from minio import Minio
from minio.sseconfig import SSEConfig
import urllib3
import os
import ssl

# ==================== Configuration ====================
minio_endpoint = "192.168.1.153:9000"   
access_key = "minioadmin"
secret_key = "minioadmin"

# CA certificate configuration
minio_ca_cert = os.path.expanduser("~/minio/certs/public.crt")            

if not os.path.isfile(minio_ca_cert):
    raise SystemExit(f"CA certificate not found: {minio_ca_cert}")

print(f"Using CA cert: {minio_ca_cert}")

# Create HTTP client with custom CA certificate
http_client = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=minio_ca_cert,
)

minio_client = Minio(
    minio_endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=True,                # Uses HTTPS
    cert_check=True,            # Verifies certificate
    http_client=http_client,    # Uses custom CA cert
)

# ==================== Test Connection ====================
print("\n" + "=" * 60)
print("MinIO Connection & Security Status")
print("=" * 60)

try:
    # Test basic connection
    buckets = minio_client.list_buckets()
    print("\n✓ CONNECTION STATUS")
    print(f"  - Server: {minio_endpoint}")
    print(f"  - Status: CONNECTED")
    print(f"  - Buckets found: {len(buckets)}")
    
    # ==================== TLS/SSL Information ====================
    print("\n✓ TLS/SSL SECURITY")
    print(f"  - Protocol: HTTPS (secure=True)")
    print(f"  - Certificate check: ENABLED")
    print(f"  - CA certificate: {os.path.basename(minio_ca_cert)}")
    print(f"  - Certificate path: {minio_ca_cert}")
    
    # ==================== Check SSE Status Per Bucket ====================
    print("\n✓ SERVER-SIDE ENCRYPTION (SSE) STATUS")
    
    sse_enabled_count = 0
    for bucket in buckets:
        bucket_name = bucket.name
        try:
            # Try to get bucket encryption config
            encryption_config = minio_client.get_bucket_encryption(bucket_name)
            if encryption_config:
                print(f"  - {bucket_name}: SSE ENABLED")
                sse_enabled_count += 1
        except Exception as e:
            # No encryption configured for this bucket
            print(f"  - {bucket_name}: SSE NOT CONFIGURED")
    
    print(f"\n  Summary: {sse_enabled_count}/{len(buckets)} bucket(s) with SSE enabled")
    
    # ==================== Bucket List ====================
    print("\n✓ BUCKETS")
    for bucket in buckets:
        print(f"  - {bucket.name} (created: {bucket.creation_date})")
    
except Exception as err:
    print(f"\n✗ Connection failed: {err}")
    raise

