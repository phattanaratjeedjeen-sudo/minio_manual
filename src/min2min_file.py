import os
import urllib3
from minio import Minio

# ==================== Configuration ====================
upstream_ip = "192.168.1.152:9000"
downstream_ip = "192.168.1.153:9000"
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "my-bucket"
object_name = "SSE_key.txt"

# CA certificate configuration
minio_ca_cert = os.path.expanduser("~/minio/certs/public.crt")    

# ==================== Secure Connection Helper ====================
def get_secure_client(endpoint, cert_path):
    # This creates a manager that TRUSTS your specific self-signed cert
    http_client = urllib3.PoolManager(
        cert_reqs="CERT_REQUIRED",
        ca_certs=cert_path
    )
    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=True,
        http_client=http_client 
    )

# --- Initialize Clients ---
try:
    up_client = get_secure_client(upstream_ip, minio_ca_cert)
    down_client = get_secure_client(downstream_ip, minio_ca_cert)
    print("✓ Connections initialized (Self-signed certs trusted)")
except Exception as e:
    print(f"✗ Setup failed: {e}")
    exit()


# ==================== The Transfer ====================
try:
    print(f"Reading {object_name} from {upstream_ip}...")
    response = up_client.get_object(bucket_name, object_name)
    
    print(f"Writing {object_name} to {downstream_ip}...")
    down_client.put_object(
        bucket_name,
        object_name,
        response,
        length=-1, 
        part_size=5*1024*1024 
    )
    print(f"✓ Success! File mirrored from {upstream_ip} to {downstream_ip}")

except Exception as err:
    print(f"✗ Transfer Failed: {err}")
finally:
    if 'response' in locals():
        response.close()
        response.release_conn()