# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock to the container
COPY Pipfile* /app/

# Install pipenv and project dependencies
RUN pip install pipenv && \
    pipenv install --system --deploy --ignore-pipfile

# Copy the rest of the project files to the container
COPY .. /app

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port on which the Flask app will run
EXPOSE 8000

# Start the Flask development server
CMD ["flask", "run"]