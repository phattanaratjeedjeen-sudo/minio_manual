import os
import urllib3
from minio import Minio
from minio.credentials import StaticProvider

# ==================== Configuration ====================
minio_endpoint = "192.168.1.152:9000"   
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "b-buck"

minio_ca_cert = os.path.expanduser("~/minio/certs/public.crt")    
http_client = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=minio_ca_cert)

try:
    minio_client = Minio(
        minio_endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=True,
        cert_check=True,
        http_client=http_client,
    )
    
    config = minio_client.get_bucket_encryption(bucket_name)
    print(f"Bucket '{bucket_name}' SSE Key:")
    print(f"  Algorithm: {config.rule.sse_algorithm}")
    print(f"  KMS Key ID: {config.rule.kms_master_key_id}")

except Exception as e:
    print(f"Failed with Admin SDK: {e}")