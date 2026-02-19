import pickle
from ultralytics import YOLO
import cv2
import numpy as np
import sys

# Force flush
sys.stdout.reconfigure(line_buffering=True)

print("START verify_yolo.py")

try:
    model_path = 'yolov8n/data.pkl'
    print(f"Loading {model_path}...")
    
    # Try pickle first as user said it's a pkl
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print("Loaded via pickle.load()")
    except Exception as e:
        print(f"Pickle load failed: {e}")
        # Try standard YOLO load
        print("Trying YOLO(path)...")
        model = YOLO(model_path)
        print("Loaded via YOLO()")

    # Create dummy image
    img = np.zeros((640, 640, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (500, 500), (255, 255, 255), -1)

    print("Running inference...")
    results = model(img, verbose=False)
    
    print(f"Results type: {type(results)}")
    
    found_any = False
    for r in results:
        names = r.names
        print(f"Class names available: {list(names.values())[:5]}...") # Print first 5
        print(f"Boxes detected: {len(r.boxes)}")
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = names[cls_id] if cls_id in names else str(cls_id)
            print(f"DETECTED: {label} ({conf:.2f})")
            found_any = True
            
    if not found_any:
        print("No objects detected in dummy image (expected for black/white rect)")
    
    print("SUCCESS: Model works")

except Exception as e:
    print(f"FAILURE: {e}")
