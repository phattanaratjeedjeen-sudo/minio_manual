import os
import urllib3
from minio.minioadmin import MinioAdmin
from minio.credentials import StaticProvider

# ==================== Configuration ====================
minio_endpoint = "192.168.1.152:9000"   
access_key = "minioadmin"
secret_key = "minioadmin"
SSE_key = "key4" 

minio_ca_cert = os.path.expanduser("~/minio/certs/public.crt")    
http_client = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=minio_ca_cert)


provider = StaticProvider(access_key, secret_key)

try:
    admin_client = MinioAdmin(
        endpoint=minio_endpoint,
        credentials=provider,
        secure=True,
        http_client=http_client
    )
    
    admin_client.kms_key_create(SSE_key)
    print(f"Successfully created/rotated KMS key: {SSE_key}")

except Exception as e:
    print(f"Failed with Admin SDK: {e}")