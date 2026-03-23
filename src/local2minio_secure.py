import os
import urllib3
from minio import Minio
from minio.error import S3Error

myhp = "192.168.1.152:9000"                    # ---------------- CHANGE TO DESIRED SERVER IP ----------------
myasus = "192.168.1.153:9000"                  

end_point = myhp                               # ---------------- CHANGE TO DESIRED ENDPOINT SERVER ----------------   

# Determine the CA certificate path of the destination MinIO server
crt_path = os.path.expanduser("~/minio/certs/")                         
crt_name = "public.crt"                        # ---------------- CHANGE TO DESIRED ENDPOINT SERVER'S CERTIFICATE ----------------
minio_ca_cert = os.path.join(crt_path, crt_name)

if not os.path.isfile(minio_ca_cert):
    raise SystemExit(f"CA certificate not found: {minio_ca_cert}")


# Create HTTP client with custom CA certificate
http_client = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=minio_ca_cert,
)

# 1. Initialize MinIO client
# Replace with your actual endpoint, access key, and secret key
minio_client = Minio(
    end_point,
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True,
    cert_check=True,
    http_client=http_client,
)

# 2. Define your local source and destination bucket
# Adjust the local_root to match your ~/dist/files/ location
local_root = os.path.expanduser("~/dist/files/")        # ---------------- CHANGE TO DESIRED LOCAL DIRECTORY ----------------
bucket = "ccr-data-drive"                               # ---------------- CHANGE TO DESIRED BUCKET ----------------

# Create bucket if it doesn't exist
try:
    if not minio_client.bucket_exists(bucket):
        print(f"Creating bucket: {bucket}")
        minio_client.make_bucket(bucket)
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

# Walk through the local directory structure
# First pass: identify and mark empty directories with .gitkeep
temp_gitkeep_files = []
for root, dirs, files in os.walk(local_root):
    # Check if this directory is empty (no files, and no subdirectories with files)
    if not files:
        gitkeep_path = os.path.join(root, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            open(gitkeep_path, 'a').close()
            temp_gitkeep_files.append(gitkeep_path)
            print(f"Created .gitkeep in {root}")

# Second pass: upload all files including .gitkeep markers
for root, dirs, files in os.walk(local_root):
    for file in files:
        # Construct the local file path
        local_file_path = os.path.join(root, file)
        
        # Construct the object name (path inside the bucket)
        # This removes the base local_path to keep the relative structure
        relative_path = os.path.relpath(local_file_path, local_root)
        # MinIO uses forward slashes for paths regardless of OS
        object_name = relative_path.replace(os.sep, '/')

        try:
            print(f"Uploading {local_file_path} to {object_name}...")
            minio_client.fput_object(
                bucket, 
                object_name, 
                local_file_path
            )
        except S3Error as err:
            print(f"Error occurred while uploading {file}: {err}")

# Clean up temporary .gitkeep files
for gitkeep_file in temp_gitkeep_files:
    try:
        os.remove(gitkeep_file)
        print(f"Cleaned up {gitkeep_file}")
    except Exception as err:
        print(f"Could not remove {gitkeep_file}: {err}")


print("Transfer complete.")