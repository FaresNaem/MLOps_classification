from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy.orm import Session

# Database connection string
DATABASE_URL = "postgresql://postgres:123@localhost:5432/postgres"

# Set up engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# User table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)  # Either 'user' or 'admin'

    # Relationship with the logs table
    logs = relationship("Log", back_populates="user")


# Product table to store product data (images, descriptions, and categories)
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)  # Path to the image file
    designation = Column(Text, nullable=False)  # Product text title
    description = Column(Text, nullable=False)  # Product text description
    category = Column(String, nullable=False)  # Product category (predicted or labeled)
    state = Column(Integer, default=0)  # state = 1 if the image has been used before for model training, 0 otherwise


# Log table for storing events such as retraining, data addition, errors, etc.
class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Who triggered the event (admin)
    event = Column(String, nullable=False)  # Event description (e.g., 'retraining', 'new data added', etc.)

    # Relationship with the User table
    user = relationship("User", back_populates="logs")


# Function to create the tables
def create_tables():
    Base.metadata.create_all(bind=engine)


# Example: Function to add a new product to the database
def add_product(session: Session, image_path: str, designation: str, description: str, category: str):
    new_product = Product(
        image_path=image_path,
        designation=designation,  # Storing the title/designation
        description=description,
        category=category
    )
    session.add(new_product)
    session.commit()


# Example: Function to log events (e.g., model retraining, data ingestion)
def log_event(session, user_id, event):
    new_log = Log(user_id=user_id, event=event)
    session.add(new_log)
    session.commit()


# Function to get a user from the database by username
def get_user(session, username: str):
    return session.query(User).filter(User.username == username).first()


# Function to create a new user in the database
def create_user(session, username: str, password_hash: str, role: str = "user"):
    # Check if the username already exists
    existing_user = get_user(session, username)
    if existing_user:
        raise ValueError(f"User with username '{username}' already exists.")
    new_user = User(username=username, password_hash=password_hash, role=role)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)  # Optional: Refresh the new_user object with the data from the database
    return new_user


def get_untrained_products(session: Session):
    """
    Retrieve all products with state = 0 (untrained products).
    """
    return session.query(Product).filter(Product.state == 0).all()


def update_product_state(session: Session, product_ids):
    """
    Update the state of products to 1 (indicating they have been used in training).
    """
    session.query(Product).filter(Product.id.in_(product_ids)).update({"state": 1}, synchronize_session='fetch')
    session.commit()


# Example usage
if __name__ == "__main__":
    # Create all tables
    create_tables()

    # Open a session
    session = SessionLocal()

    try:
        # Create a new user
        user = create_user(session, "mahatma", "mahatmahashed_password2", "user")

        # Add a new product
        add_product(session, "prod2.jpg", "A great product2", "electronics2", '3')

        # Log an event
        log_event(session, user.id, "Added a new product")

        # Fetch user by username
        fetched_user = get_user(session, "john_doe2")
        print(f"Fetched user: {fetched_user.username}")

    finally:
        # Close the session
        session.close()
