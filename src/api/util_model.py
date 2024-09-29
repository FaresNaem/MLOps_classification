import numpy as np
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow import expand_dims, convert_to_tensor, float32
from tensorflow.keras.applications.efficientnet import preprocess_input
from PIL import Image, ImageOps


# Function to preprocess image
def preprocess_image(image, target_size=(224, 224)):
    image = ImageOps.fit(image, target_size, Image.LANCZOS)
    image = np.array(image) / 255.0
    image = convert_to_tensor(image, dtype=float32)
    image = preprocess_input(image)
    return expand_dims(image, axis=0)


def predict_classification(model, vectorizer, designation: str, description: str, image: Image.Image):
    # Preprocess text data
    text_data = designation + ' ' + description
    processed_text = vectorizer.transform([text_data]).toarray()

    # Preprocess image data (no need to re-open the image)
    processed_image = preprocess_image(image)

    # Extract image features using EfficientNetB0
    image_features = EfficientNetB0(weights='imagenet', include_top=False)(processed_image)
    image_features = GlobalAveragePooling2D()(image_features).numpy()

    # Perform prediction
    prediction = model.predict([processed_text, image_features])
    predicted_class = np.argmax(prediction, axis=1)

    # Get confidence score (maximum probability)
    confidence = np.max(prediction, axis=1)

    return {'predicted_class': predicted_class, 'confidence': confidence}
