from ultralytics import YOLO
import pickle
import sys

sys.stdout.reconfigure(line_buffering=True)

print("Checking model classes...")
model_path = 'yolov8n/data.pkl'

try:
    print(f"Attempting valid load of {model_path}...")
    # Try generic load
    model = YOLO(model_path)
    print(f"Model loaded. Classes found: {len(model.names)}")
    print(f"First 10 classes: {list(model.names.values())[:10]}")
    
    restricted = ['cell phone', 'laptop', 'book', 'tv']
    print(f"Checking restricted: {restricted}")
    
    found = [r for r in restricted if r in model.names.values()]
    print(f"Found restricted classes in model: {found}")

except Exception as e:
    print(f"Error: {e}")
    print("Trying fallback to standard yolov8n.pt")
    model = YOLO("yolov8n.pt")
    print(f"Fallback classes: {list(model.names.values())[:10]}")
