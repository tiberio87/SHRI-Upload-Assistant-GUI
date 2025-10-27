FROM python:3.12

# Update the package list and install system dependencies including mono
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    g++ \
    cargo \
    mktorrent \
    mediainfo \
    rustc \
    mono-complete \
    nano && \
    rm -rf /var/lib/apt/lists/*

# Set up a virtual environment to isolate our Python dependencies
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install wheel, requests (for DVD MediaInfo download), and other Python dependencies
RUN pip install --upgrade pip wheel requests

# Set the working directory in the container
WORKDIR /Upload-Assistant

# Copy DVD MediaInfo download script and run it
# This downloads specialized MediaInfo binaries for DVD processing with language support
COPY bin/get_dvd_mediainfo_docker.py bin/
RUN python3 bin/get_dvd_mediainfo_docker.py

# Copy the Python requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the download script
COPY bin/download_mkbrr_for_docker.py bin/
RUN chmod +x bin/download_mkbrr_for_docker.py

# Download only the required mkbrr binary
RUN python3 bin/download_mkbrr_for_docker.py

# Copy the rest of the application
COPY . .

# Ensure mkbrr is executable
RUN find bin/mkbrr -type f -name "mkbrr" -exec chmod +x {} \;

# Create tmp directory with appropriate permissions
RUN mkdir -p /Upload-Assistant/tmp && chmod 777 /Upload-Assistant/tmp
ENV TMPDIR=/Upload-Assistant/tmp

# Set the entry point for the container
ENTRYPOINT ["python", "/Upload-Assistant/upload.py"]