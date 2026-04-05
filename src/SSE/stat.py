from minio import Minio
import urllib3
import os
from datetime import datetime, timezone

# ==================== Configuration ====================
minio_endpoint = "192.168.1.152:9000"   
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "a-buck"

minio_ca_cert = os.path.expanduser("~/minio/certs/public.crt")    
http_client = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=minio_ca_cert)

client = Minio(
    endpoint=minio_endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=True,
    cert_check=True,
    http_client=http_client
)

def format_size(size):
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.0f} {unit}" if unit == 'B' else f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def format_date(dt):
    """Format datetime to match mc stat output."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local_dt = dt.astimezone()
    return local_dt.strftime("%Y-%m-%d %H:%M:%S %z").replace("+07", "+07 ")

try:
    # List all objects in bucket
    objects = client.list_objects(bucket_name, recursive=True)
    
    for obj in objects:
        # Get detailed object information
        stat_info = client.stat_object(bucket_name, obj.object_name)
        metadata = stat_info.metadata
        
        print(f"Name      : {obj.object_name}")
        print(f"Date      : {format_date(obj.last_modified)}")
        print(f"Size      : {format_size(obj.size):>5}")
        print(f"ETag      : {obj.etag}")
        print(f"Type      : file")
        
        # Checksum (CRC64)
        if 'X-Minio-Checksum-Crc64ecma' in metadata:
            print(f"Checksum  : CRC64NVME:{metadata['X-Minio-Checksum-Crc64ecma']}")
        
        # Encryption
        sse_type = metadata.get('X-Amz-Server-Side-Encryption', '')
        if sse_type:
            kms_key = metadata.get('X-Amz-Server-Side-Encryption-Aws-Kms-Key-Id', '')
            if kms_key:
                print(f"Encryption: {sse_type}-KMS ({kms_key})")
            else:
                print(f"Encryption: {sse_type}")
        
        # Metadata
        content_type = metadata.get('Content-Type', '')
        if content_type:
            print(f"Metadata  :")
            print(f"  Content-Type: {content_type}")
        
        print()  # Blank line between objects

except Exception as e:
    print(f"Failed with Admin SDK: {e}")
    import traceback
    traceback.print_exc()

