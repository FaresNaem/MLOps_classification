from fastapi import FastAPI, UploadFile, File, Form
from fastapi import Depends, HTTPException
from joblib import load as joblib_load
from tensorflow.keras.models import load_model
import os
from util_model import predict_classification
from PIL import Image
from io import BytesIO
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import GlobalAveragePooling2D
import numpy as np
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import create_user, get_user, add_product
from database import SessionLocal  # Import the session maker
from util_auth import create_access_token, verify_password, get_password_hash, verify_access_token, admin_required
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends, Request
from uuid import uuid4

# Load vectorizer and model globally when the app starts
vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'Tfidf_vectorizer.joblib')
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'retrained_balanced_model.keras')

vectorizer = joblib_load(vectorizer_path)
model = load_model(model_path)


# Dependency to get a session from the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize OAuth2PasswordBearer to extract access token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/signup")
async def signup(username: str, password: str, db: Session = Depends(get_db)):
    # Check if the username already exists in the database
    existing_user = get_user(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # If the username doesn't exist, create the new user
    hashed_password = get_password_hash(password)
    create_user(db, username, hashed_password)

    return {"message": "User created successfully"}


@app.post("/predict")
async def predict_category(
        token: str = Depends(oauth2_scheme),  # Authentication dependency
        designation: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...)
):
    # Verify the access token
    user_info = verify_access_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # If token is valid, proceed with prediction
    image_data = await file.read()
    image = Image.open(BytesIO(image_data))

    # Call the prediction function
    predicted_class = predict_classification(model, vectorizer, designation, description, image)

    return {"predicted_class": int(predicted_class[0])}


@app.get("/admin-only")
@admin_required()
async def admin_route(request: Request, db: Session = Depends(get_db)):
    return {"message": "Welcome, admin!"}


# Define a directory to store uploaded images
UPLOAD_DIR = r"C:\Users\user\Documents\DS_WB\images_uploaded"


@app.post("/add-product-data")
@admin_required()  # Decorator checks for admin privileges
async def add_product_api(
        request: Request,  # Add request parameter
        session: Session = Depends(get_db),  # Database session dependency
        image: UploadFile = File(...),
        designation: str = Form(...),  # 'designation' as a product title
        description: str = Form(...),
        category: str = Form(...)
):
    # Generate a unique filename using UUID and preserve the original file extension
    file_extension = os.path.splitext(image.filename)[1]
    image_filename = f"{uuid4()}{file_extension}"
    image_path = os.path.join(UPLOAD_DIR, image_filename)

    try:
        # Ensure the upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save the image to the specified directory
        with open(image_path, "wb") as f:
            f.write(await image.read())

        # Call the function to add product data to the database
        add_product(session, image_path, designation, description, category)

        # Return a successful response
        return {"message": "Product added successfully"}
    except Exception as e:
        # If an error occurs, raise an HTTPException
        raise HTTPException(status_code=500, detail=f"Error saving product: {str(e)}")
