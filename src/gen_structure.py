import os

def create_test_files(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # If it's a dictionary, it's a folder
            os.makedirs(path, exist_ok=True)
            create_test_files(path, content)
        else:
            # If it's a list, it's a list of files in this folder
            os.makedirs(path, exist_ok=True)
            for file_name in content:
                file_path = os.path.join(path, file_name)
                # Create a 1KB file (1024 bytes)
                with open(file_path, "wb") as f:
                    f.write(os.urandom(1024))
                print(f"Created: {file_path} (1KB)")

# Define the extracted structure from your image
pcd_files = ["CornerMap.bin", "cover.webp", "GlobalMap.bin", "info.json", "SurfMap.bin", "web.bin"]

ccr_structure = {
    "pcds": {
        "pcd_fibo_floor6": pcd_files,
        "pcd_kmutt_football": [],
        "pcd_fibo_outdoor": []
    },
    "topoSingle": {
        "topo_fibo_floor6": {
            ".": ["cover.webp", "data.json"], # Files in topo_fibo_floor6 root
            "pcds": {
                "pcd_fibo_floor6": pcd_files
            }
        },
        "topo_kmutt_football": [],
        "topo_fibo_outdoor": []
    },
    "inspection": {
        "inspection_fibo_floor6": {
            ".": ["data.json"],
            "images": [
                "inspection_fibo_6-p1.png", 
                "inspection_fibo_6-p2.png", 
                "inspection_fibo_6-p3.png"
            ]
        },
        "inspection_fibo_outdoor": [],
        "inspection_indoor": []
    },
    "gps": []
}

if __name__ == "__main__":
    # Define your local test root
    target_directory = os.path.expanduser("~/dist/files/")
    
    print(f"Starting creation in: {target_directory}")
    create_test_files(target_directory, ccr_structure)
    print("\nTest structure created successfully.")