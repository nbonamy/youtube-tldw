# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# config file
RUN echo "[General]\nollama_url=http://host.docker.internal:11434" > youtube-tldw.conf

# Make port 80 available to the world outside this container
EXPOSE 5555

# Run app.py when the container launches
CMD ["python", "./src/app.py"]
