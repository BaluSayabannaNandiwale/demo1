import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras

class _DummyLandmarkModel:
    """Fallback model used when the real landmark model cannot be loaded."""

    def __init__(self):
        # Expose a SavedModel-like signatures dict
        self.signatures = {"predict": self._predict}

    @tf.function
    def _predict(self, inputs):
        # inputs is expected to be a 4D tensor [batch, h, w, c]
        batch_size = tf.shape(inputs)[0]
        # Return zeros for 68 (x, y) landmarks => 136 values
        return {"output": tf.zeros((batch_size, 136), dtype=tf.float32)}


def get_landmark_model(saved_model="models/pose_model"):
    """
    Load the facial landmark model in a way that works with both
    older Keras versions and Keras 3. If loading fails (e.g. missing
    variables or incompatible format), a lightweight dummy model is
    returned so the rest of the application can continue running.
    """
    # Try Keras loader first
    try:
        return keras.models.load_model(saved_model)
    except Exception as e1:
        print(f"Warning: keras.models.load_model failed for {saved_model}: {e1}")

    # Try TensorFlow SavedModel loader
    try:
        return tf.saved_model.load(saved_model)
    except Exception as e2:
        print(f"Warning: tf.saved_model.load failed for {saved_model}: {e2}")
        print("Using dummy landmark model; head pose estimation may be degraded.")
        return _DummyLandmarkModel()

def get_square_box(box):
    left_x = box[0]
    top_y = box[1]
    right_x = box[2]
    bottom_y = box[3]

    box_width = right_x - left_x
    box_height = bottom_y - top_y

    diff = box_height - box_width
    delta = int(abs(diff) / 2)

    if diff == 0:                   # Already a square.
        return box
    elif diff > 0:                  # Height > width, a slim box.
        left_x -= delta
        right_x += delta
        if diff % 2 == 1:
            right_x += 1
    else:                           # Width > height, a short box.
        top_y -= delta
        bottom_y += delta
        if diff % 2 == 1:
            bottom_y += 1

    assert ((right_x - left_x) == (bottom_y - top_y)), 'Box is not square.'

    return [left_x, top_y, right_x, bottom_y]

def move_box(box, offset):
        left_x = box[0] + offset[0]
        top_y = box[1] + offset[1]
        right_x = box[2] + offset[0]
        bottom_y = box[3] + offset[1]
        return [left_x, top_y, right_x, bottom_y]

def detect_marks(img, model, face):
    offset_y = int(abs((face[3] - face[1]) * 0.1))
    box_moved = move_box(face, [0, offset_y])
    facebox = get_square_box(box_moved)
    
    h, w = img.shape[:2]
    if facebox[0] < 0:
        facebox[0] = 0
    if facebox[1] < 0:
        facebox[1] = 0
    if facebox[2] > w:
        facebox[2] = w
    if facebox[3] > h:
        facebox[3] = h
    
    face_img = img[facebox[1]: facebox[3],
                     facebox[0]: facebox[2]]
    face_img = cv2.resize(face_img, (320, 320))
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    
    predictions = model.signatures["predict"](
        tf.constant([face_img], dtype=tf.uint8))

    marks = np.array(predictions['output']).flatten()[:136]
    marks = np.reshape(marks, (-1, 2))
    
    marks *= (facebox[2] - facebox[0])
    marks[:, 0] += facebox[0]
    marks[:, 1] += facebox[1]
    marks = marks.astype(np.uint)

    return marks