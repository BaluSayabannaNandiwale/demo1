#!/usr/bin/env python
"""
Script to download required model files for the proctoring system
"""

import os
import wget
import sys

def download_yolo_weights():
    """Download YOLOv3 weights file if it doesn't exist"""
    import requests
    weights_path = "models/yolov3.weights"
    
    if os.path.exists(weights_path):
        print(f"YOLOv3 weights already exist at {weights_path}")
        return True
    
    print("Downloading YOLOv3 weights...")
    # Try multiple sources for YOLOv3 weights
    urls = [
        "https://github.com/shadiakiki1986/yolov3.weights/releases/download/3.0.1/yolov3.weights",
        "https://pjreddie.com/media/files/yolov3.weights",
        "https://sourceforge.net/projects/yolov3.mirror/files/v8/yolov3.weights/download"
    ]
    
    for url in urls:
        try:
            print(f"Trying to download from: {url}")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(weights_path, 'wb') as f:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\rDownload progress: {percent:.1f}%", end='', flush=True)
                
                print(f"\nSuccessfully downloaded YOLOv3 weights to {weights_path}")
                return True
        except Exception as e:
            print(f"\nFailed to download from {url}: {e}")
            continue
    
    print("All download attempts failed.")
    return False

def main():
    print("Starting model downloads...")
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Download YOLOv3 weights
    if not download_yolo_weights():
        print("Could not download required model files. Exiting.")
        sys.exit(1)
    
    print("All required models downloaded successfully!")

if __name__ == "__main__":
    main()