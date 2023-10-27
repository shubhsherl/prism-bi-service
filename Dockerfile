# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of your FastAPI application's code into the container
COPY . .

# Expose the port your FastAPI app will run on
EXPOSE 8000

# Set permissions for the start script
RUN chmod +x ./start.sh

# Define the command to run your the start script
CMD ["./start.sh"]
