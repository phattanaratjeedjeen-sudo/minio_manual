import os
import urllib3
from minio import Minio
from minio.error import S3Error

myhp = "192.168.1.152:9000"                         # ---------------- CHANGE TO DESIRED SERVER IP ----------------
myasus = "192.168.1.153:9000"

end_point = myhp                                    # ---------------- CHANGE TO DESIRED ENDPOINT SERVER ----------------

# Determine the CA certificate path of upstream MinIO server
crt_path = os.path.expanduser("~/minio/certs/")
crt_name = "public.crt"                             # ---------------- CHANGE TO DESIRED ENDPOINT SERVER'S CERTIFICATE ----------------
minio_ca_cert = os.path.join(crt_path, crt_name)

if not os.path.isfile(minio_ca_cert):
    raise SystemExit(f"CA certificate not found: {minio_ca_cert}")


# Create HTTP client with custom CA certificate
http_client = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=minio_ca_cert,
)

# 1. Initialize MinIO client
minio_client = Minio(
    end_point,
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True,
    cert_check=True,
    http_client=http_client,
)

# 2. Define your destination and source bucket
local_root = os.path.expanduser("~/m2l/dist/files/")    # ---------------- CHANGE TO DESIRED LOCAL DIRECTORY ----------------
bucket = "ccr-data-drive"                               # ---------------- CHANGE TO DESIRED BUCKET ----------------

# Create local directory if it doesn't exist
os.makedirs(local_root, exist_ok=True)

# List and download all objects from the bucket
try:
    objects = minio_client.list_objects(bucket, recursive=True)
    for obj in objects:
        object_name = obj.object_name
        local_file_path = os.path.join(local_root, object_name)
        
        # Create directories for nested objects
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        
        try:
            print(f"Downloading {object_name} to {local_file_path}...")
            minio_client.fget_object(bucket, object_name, local_file_path)
        except S3Error as err:
            print(f"Error occurred while downloading {object_name}: {err}")
    
    # Clean up .gitkeep files to restore original directory structure
    print("\nCleaning up .gitkeep placeholder files...")
    for root, dirs, files in os.walk(local_root):
        if '.gitkeep' in files:
            gitkeep_path = os.path.join(root, '.gitkeep')
            try:
                os.remove(gitkeep_path)
                print(f"Removed {gitkeep_path}")
            except Exception as err:
                print(f"Could not remove {gitkeep_path}: {err}")
except Exception as err:
    err_msg = str(err)
    if "CERTIFICATE_VERIFY_FAILED" in err_msg:
        hints = [
            "TLS certificate verification failed.",
            "Keep cert_check=True and provide your CA cert with MINIO_CA_CERT=/path/to/ca.crt",
        ]
        if "IP address mismatch" in err_msg or "Hostname mismatch" in err_msg:
            hints.append(
                "Endpoint hostname/IP does not match certificate SAN/CN. Use a hostname/IP present in the certificate."
            )
        raise SystemExit("\n".join(hints) + f"\nOriginal error: {err_msg}")
    raise

print("Transfer complete.")
