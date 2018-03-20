# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /app
WORKDIR /app


# Install processing utilities - GhostScript, ImageMagick (ver 6.x.x), Magick Wand
RUN apt-get update && apt-get install -y \
  imagemagick \
  libmagickwand-dev \
  ghostscript

# Copy the current directory static contents into the container at /app
ADD ./*.txt /app/
ADD ./*.pdf /app/

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the code files last, for faster iterative updates
ADD ./*.py /app/

# Make port 80 available to the world outside this container
EXPOSE 80
EXPOSE 4000

# Define environment variable
ENV NAME Dev

CMD ["python", "test_chopper.py"]
CMD ["python", "test_storeybook.py"]

# Run app.py when the container launches
CMD ["python", "host.py"]
