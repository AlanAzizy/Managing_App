# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container to /app/managing_product
WORKDIR /app/managing_product

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed dependencies from the requirements file located at /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server (or Gunicorn for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
