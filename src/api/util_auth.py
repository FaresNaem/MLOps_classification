from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, Request
from database import get_user, SessionLocal
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # Get the 'sub' field from the token (user's username)
        if username is None:
            return None
        return {"username": username}
    except JWTError:
        return None


from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, Request
from database import get_user, SessionLocal
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


# Password hash utility
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# JWT utility to create a token
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# JWT utility to verify a token
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # Get the 'sub' field from the token (user's username)
        if username is None:
            return None
        return {"username": username}
    except JWTError:
        return None


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Decorator to check if the user is admin
def admin_required():
    def decorator(func):
        async def wrapper(request: Request, db: Session = Depends(get_db)):
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                raise HTTPException(status_code=403, detail="Not authenticated")

            token = token[len("Bearer "):]  # Extract the actual token part
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str = payload.get("sub")
                if username is None:
                    raise HTTPException(status_code=403, detail="Invalid token")

                # Get user from the database
                user = get_user(db, username)
                if not user:
                    raise HTTPException(status_code=403, detail="User not found")

                # Check if the user is an admin
                if user.role != "admin":
                    raise HTTPException(status_code=403, detail="Not authorized")

            except JWTError:
                raise HTTPException(status_code=403, detail="Not authenticated")

            # Proceed with the wrapped function
            return await func(request, db)

        return wrapper

    return decorator


if __name__ == "__main__":
    # Test examples
    # 1. Hash a password
    password = "my_secure_password"
    hashed_password = get_password_hash(password)
    print(f"Original Password: {password}")
    print(f"Hashed Password: {hashed_password}")

    # 2. Verify the hashed password
    is_verified = verify_password("my_secure_password", hashed_password)
    print(f"Password Verified: {is_verified}")  # Should print: True

    # 3. Test with an incorrect password
    is_verified_incorrect = verify_password("wrong_password", hashed_password)
    print(f"Password Verified (incorrect): {is_verified_incorrect}")  # Should print: False

    # 4. Create a JWT access token
    token_data = {"sub": "user@example.com"}
    access_token = create_access_token(token_data)
    print(f"Access Token: {access_token}")

    # 5. Decode the token (for testing purposes)
    # Note: Decoding should be done using the same library that created the token.
    try:
        decoded_data = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded Token Data: {decoded_data}")
    except JWTError as e:
        print(f"Error decoding token: {str(e)}")
