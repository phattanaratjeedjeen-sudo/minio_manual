import urllib3
from minio import Minio
from minio.error import S3Error

myhp = "192.168.1.152:9000"
myasus = "192.168.1.153:9000"
bucket = "ccr-data-drive"

minio_client = Minio(
    myhp,  # S3 API endpoint
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True,
    cert_check=False,
)

# Suppress warning because cert_check=False is intentionally used with self-signed cert.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    if not minio_client.bucket_exists(bucket):
        print(f"Bucket does not exist: {bucket}")
        raise SystemExit(0)

    deleted_count = 0
    for obj in minio_client.list_objects(bucket, recursive=True, include_version=True):
        minio_client.remove_object(bucket, obj.object_name, version_id=obj.version_id)
        deleted_count += 1

    minio_client.remove_bucket(bucket)
    print(f"Bucket deleted: {bucket} (removed {deleted_count} object/version entries first)")
except S3Error as err:
    print(f"Delete bucket failed: {err}")
    raise