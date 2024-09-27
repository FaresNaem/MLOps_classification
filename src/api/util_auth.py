from passlib.context import CryptContext
from jose import JWTError, jwt

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


"""   
# Decorator to check if user is admin
def admin_required():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            token = kwargs.get("token")
            if not token:
                raise HTTPException(status_code=403, detail="Not authenticated")
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str = payload.get("sub")
                user = get_user(next(get_db()), username)
                if user.role != "admin":
                    raise HTTPException(status_code=403, detail="Not authorized")
            except JWTError:
                raise HTTPException(status_code=403, detail="Not authenticated")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

"""

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
