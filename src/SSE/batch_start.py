import os
import subprocess

# ==================== Configuration ====================
minio_alias = "myhp"         # your MinIO alias (configured in mc)
yaml_file = "rotate.yaml"    # path to batch YAML file

try:
    # Check if YAML file exists
    if not os.path.exists(yaml_file):
        raise FileNotFoundError(f"Batch file not found: {yaml_file}")
    
    print(f"Starting batch job from: {yaml_file}")
    
    # Run: mc batch start myhp rotate.yaml
    result = subprocess.run(
        ['mc', 'batch', 'start', minio_alias, yaml_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print(f"Status Code: {result.returncode}")
    print(f"Output:\n{result.stdout}")
    
    if result.stderr:
        print(f"Error Output:\n{result.stderr}")
    
    if result.returncode == 0:
        print("\nBatch job started successfully!")
    else:
        print(f"\nBatch job failed with exit code: {result.returncode}")
    
except FileNotFoundError as e:
    print(f"Error: {e}")
except subprocess.TimeoutExpired:
    print("Error: Command timed out")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
