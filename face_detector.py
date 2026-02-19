import cv2
import numpy as np
import os

def get_face_detector(modelFile=None,
                      configFile=None,
                      quantized=False):
    if quantized:
        if modelFile == None:
            modelFile = "models/opencv_face_detector_uint8.pb"
        if configFile == None:
            configFile = "models/opencv_face_detector.pbtxt"
        model = cv2.dnn.readNetFromTensorflow(modelFile, configFile)
        
    else:
        if modelFile == None:
            modelFile = "models/res10_300x300_ssd_iter_140000.caffemodel"
        if configFile == None:
            configFile = "models/deploy.prototxt"
        # If the Caffe-based model is not available, gracefully fall back to
        # the bundled TensorFlow face detector so the system can still run.
        if (not os.path.exists(modelFile)) or (not os.path.exists(configFile)):
            tf_model = "models/opencv_face_detector_uint8.pb"
            tf_config = "models/opencv_face_detector.pbtxt"
            if os.path.exists(tf_model) and os.path.exists(tf_config):
                return cv2.dnn.readNetFromTensorflow(tf_model, tf_config)
        model = cv2.dnn.readNetFromCaffe(configFile, modelFile)
    return model

def find_faces(img, model):
    h, w = img.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0,
	(300, 300), (104.0, 177.0, 123.0))
    model.setInput(blob)
    res = model.forward()
    faces = []
    for i in range(res.shape[2]):
        confidence = res[0, 0, i, 2]
        if confidence > 0.5:
            box = res[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x1, y1) = box.astype("int")
            faces.append([x, y, x1, y1])
    return faces