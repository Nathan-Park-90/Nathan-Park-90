# Use a Python 3.12 base image
FROM python:3.12

# Install ffmpeg and libsndfile1
RUN apt-get update && apt-get install -y ffmpeg libsndfile1

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Define the command to run the Flask app
CMD ["python", "app.py"]
