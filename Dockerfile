# Step 1: Use an official Python runtime as a base image
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the current directory contents (excluding files in .dockerignore) into the container
COPY . /app

# Step 4: Install dependencies from the requirements.txt file
RUN pip3 install -r requirements.txt

# Step 5: Expose the port your app will be running on (8501 for Streamlit)
EXPOSE 8501


# Step 7: Define the command to run your app (Streamlit or Flask app)
CMD ["streamlit", "run", "app.py"]
