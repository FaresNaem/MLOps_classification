from joblib import load as joblib_load
from tensorflow.keras.models import load_model
import os
from util_model import preprocess_image
from PIL import Image
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D
import numpy as np


def predict_classification(designation, description, image_path):
    # Define paths to the vectorizer and model
    vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'Tfidf_vectorizer.joblib')
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'retrained_balanced_model.keras')

    # Load the vectorizer and model
    vectorizer = joblib_load(vectorizer_path)
    model = load_model(model_path)

    # Preprocess text data
    text_data = designation + ' ' + description
    processed_text = vectorizer.transform([text_data]).toarray()

    # Preprocess image data
    image = Image.open(image_path)
    processed_image = preprocess_image(image)

    # Extract image features using EfficientNetB0
    image_features = EfficientNetB0(weights='imagenet', include_top=False)(processed_image)
    image_features = GlobalAveragePooling2D()(image_features).numpy()

    # Perform prediction
    prediction = model.predict([processed_text, image_features])
    predicted_class = np.argmax(prediction, axis=1)

    return predicted_class

# Example usage:
# classification_result = predict_classification("hello", "this is my product", 'POC_0.jpg')
# print(f"classification result is: {classification_result}")
if __name__ == "__main__":
    # Example usage
    designation = "hello"
    description = "this is my product"
    image_path = '../POC_0.jpg'

    # Call the function and print the result
    classification_result = predict_classification(designation, description, image_path)
    print(f"Classification result is: {classification_result}")