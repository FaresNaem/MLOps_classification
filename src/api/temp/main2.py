from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from pydantic import BaseModel
import os
from tensorflow.keras.models import load_model
from joblib import load as joblib_load
from util_model import multimodal_predict  # Import multimodal_predict function
from typing import Optional

app = FastAPI()

# Declare global variables for model and vectorizer
model = None
vectorizer = None

# Load the model and vectorizer on startup
@app.on_event("startup")
async def load_resources():
    global model, vectorizer

    # Load the model from a relative path
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'retrained_balanced_model.keras')
    model = load_model(model_path)

    # Load the TF-IDF vectorizer
    vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'Tfidf_vectorizer.joblib')
    vectorizer = joblib_load(vectorizer_path)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
