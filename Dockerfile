# 1. Use a standard Python image (not slim, to avoid missing tools)
FROM python:3.9

# 2. Update and install basic tools
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Google Chrome directly (No keys needed)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

# 4. Set the working folder
WORKDIR /app

# 5. Copy your project files
COPY . .

# 6. Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 7. Start the app
CMD ["python", "live.py"]
