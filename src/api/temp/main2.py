from fastapi import FastAPI, UploadFile, File, Form
from joblib import load as joblib_load
from tensorflow.keras.models import load_model
import os
from util_model import predict_classification
from PIL import Image
from io import BytesIO
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D
import numpy as np

app = FastAPI()

# Load vectorizer and model globally when the app starts
vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'Tfidf_vectorizer.joblib')
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'retrained_balanced_model.keras')

vectorizer = joblib_load(vectorizer_path)
model = load_model(model_path)


@app.post("/predict")
async def predict_category(
        designation: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...)
):
    # Read the image from the uploaded file
    image_data = await file.read()
    image = Image.open(BytesIO(image_data))

    # Call the prediction function
    predicted_class = predict_classification(model, vectorizer, designation, description, image)

    return {"predicted_class": int(predicted_class[0])}
