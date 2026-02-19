#!/usr/bin/env python
"""
Verification script to confirm all components of the proctoring system are working
"""

import sys
import os

def verify_dependencies():
    """Verify that all required dependencies are available"""
    print("Verifying dependencies...")
    
    dependencies = [
        ("Django", "django"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("TensorFlow", "tensorflow"),
        ("NLTK", "nltk"),
        ("deepface", "deepface"),
        ("Pillow", "PIL"),
        ("wget", "wget"),
        ("coolname", "coolname"),
    ]
    
    missing_deps = []
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[MISSING] {name}")
            missing_deps.append((name, module))
    
    return len(missing_deps) == 0

def verify_models():
    """Verify that required model files exist"""
    print("\nVerifying model files...")
    
    model_files = [
        "models/yolov3.weights",
        "models/opencv_face_detector_uint8.pb",
        "models/opencv_face_detector.pbtxt",
        "models/deploy.prototxt",
        "models/classes.TXT",
        "models/pose_model",
    ]
    
    missing_models = []
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"[OK] {model_file}")
        else:
            print(f"[MISSING] {model_file}")
            missing_models.append(model_file)
    
    return len(missing_models) == 0

def verify_core_modules():
    """Verify that core modules can be imported"""
    print("\nVerifying core modules...")
    
    modules = [
        ("face_detector", "face_detector"),
        ("face_landmarks", "face_landmarks"),
        ("camera", "camera"),
        ("objective", "objective"),
        ("subjective", "subjective"),
    ]
    
    missing_modules = []
    for name, module in modules:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError as e:
            print(f"[MISSING] {name} - {e}")
            missing_modules.append((name, module))
    
    return len(missing_modules) == 0

def main():
    # Use plain ASCII for compatibility with Windows terminals
    print("Proctoring System Verification")
    print("=" * 50)
    
    deps_ok = verify_dependencies()
    models_ok = verify_models()
    modules_ok = verify_core_modules()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Dependencies: {'OK' if deps_ok else 'MISSING'}")
    print(f"Models: {'OK' if models_ok else 'MISSING'}")
    print(f"Core Modules: {'OK' if modules_ok else 'MISSING'}")
    
    if deps_ok and models_ok and modules_ok:
        print("\nAll systems verified! The proctoring system is ready to run.")
        print("Run 'python manage.py runserver' to start the application.")
        return True
    else:
        print("\nSome components are missing. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)