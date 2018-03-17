# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD ./chopper /app/chopper
ADD ./*.txt /app/
ADD ./*.py /app/

# Install ImageMagick (uncomment for the fun)
#RUN apt-get update && apt-get install -y \
#  imagemagick

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt


# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "host.py"]