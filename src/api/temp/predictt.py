
from joblib import load as joblib_load
from tensorflow.keras.models import load_model
import os
from util_model import preprocess_image
from PIL import Image
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D
import numpy as np

def predict_classification(designation: str, description: str, image: Image.Image):
    # Preprocess text data
    text_data = designation + ' ' + description
    processed_text = vectorizer.transform([text_data]).toarray()

    # Preprocess image data (directly using the provided image object)
    processed_image = preprocess_image(image)

    # Extract image features using EfficientNetB0
    image_features = EfficientNetB0(weights='imagenet', include_top=False)(processed_image)
    image_features = GlobalAveragePooling2D()(image_features).numpy()

    # Perform prediction
    prediction = model.predict([processed_text, image_features])
    predicted_class = np.argmax(prediction, axis=1)

    return predicted_class
