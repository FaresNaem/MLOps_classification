
from joblib import load as joblib_load
from tensorflow.keras.models import load_model
import os
from util_model import preprocess_image
from PIL import Image, ImageOps
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D
import numpy as np


vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'Tfidf_vectorizer.joblib')
vectorizer = joblib_load(vectorizer_path)

# Load the model from a relative path
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'retrained_balanced_model.keras')
model = load_model(model_path)
# Display the model's summary
model.summary()

# Preprocess text data
designation = "hello"
description = "this is my product"
text_data = designation + ' ' + description
processed_text = vectorizer.transform([text_data]).toarray()

# Preprocess image data
image = Image.open('../POC_0.jpg')
processed_image = preprocess_image(image)

# Extract image features using EfficientNetB0
image_features = EfficientNetB0(weights='imagenet', include_top=False)(processed_image)
image_features = GlobalAveragePooling2D()(image_features).numpy()

# Perform prediction
prediction = model.predict([processed_text, image_features])
predicted_class = np.argmax(prediction, axis=1)

print(f"classification result is: {predicted_class}")

