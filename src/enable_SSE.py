from minio import Minio
from minio.sseconfig import SSEConfig, Rule 
import urllib3
import os

# ==================== Configuration ====================
minio_endpoint = "192.168.1.152:9000"   
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "a-buck"                


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
    # 1. Create the Rule object directly (Not SSEConfig.Rule)
    # This specifically targets your KMS master key
    kms_rule = Rule.new_sse_kms_rule("object-store-primary-default-key")

    # 2. Wrap that rule inside the SSEConfig object
    config = SSEConfig(kms_rule)

    # 3. Apply it to the bucket
    minio_client.set_bucket_encryption(
        bucket_name=bucket_name,
        config=config
    )
    print("SSE-KMS enabled successfully")

except Exception as e:
    print(f"Failed to set encryption: {e}")

