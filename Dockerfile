# Use official Python base image with the appropriate version
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to install dependencies
COPY requirements.txt .

# Install the necessary Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .

# Set environment variables (if necessary, e.g., for database)
ENV DATABASE_URL=postgresql://postgres:123@db:5432/postgres

# Expose the port that the FastAPI app will run on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
