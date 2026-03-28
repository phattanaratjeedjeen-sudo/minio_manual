"""
List bucket tree in MinIO with tree structure display
"""

import os
import urllib3
from minio import Minio
from collections import defaultdict


# ==================== Configuration ====================
minio_endpoint = "192.168.1.152:9000" 
access_key = "minioadmin"
secret_key = "minioadmin"
bucket_name = "my-bucket" 

# CA certificate configuration
minio_ca_cert = os.path.expanduser("~/minio/certs/public.crt")    


# ==================== Tree Display Functions ====================
class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = {}
        self.is_file = False
    
    def add_child(self, name):
        if name not in self.children:
            self.children[name] = TreeNode(name)
        return self.children[name]
    
    def display(self, prefix="", is_last=True):
        """Display tree node with proper formatting"""
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{self.name}")
        
        extension = "    " if is_last else "│   "
        children_list = sorted(self.children.items())
        
        for i, (name, child) in enumerate(children_list):
            is_last_child = (i == len(children_list) - 1)
            child.display(prefix + extension, is_last_child)


# ==================== List Bucket Tree ====================
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

# List bucket tree
try:
    if minio_client.bucket_exists(bucket_name):
        print(f"✓ Bucket '{bucket_name}'\n")
        
        # Build tree structure
        root = TreeNode(bucket_name)
        
        for obj in minio_client.list_objects(bucket_name, recursive=True):
            path_parts = obj.object_name.split('/')
            current_node = root
            
            # Navigate/create tree structure
            for i, part in enumerate(path_parts):
                if part:  # Skip empty parts
                    current_node = current_node.add_child(part)
        
        # Display tree
        for name, child in sorted(root.children.items()):
            is_last = (name == sorted(root.children.keys())[-1])
            child.display("", is_last)
    else:
        print(f"✗ Bucket '{bucket_name}' does not exist")
except Exception as err:
    print(f"✗ Error: {err}")
    raise
