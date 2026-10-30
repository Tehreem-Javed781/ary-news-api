FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    REGISTRATION=FA23-BDS-041

# Google Chrome (stable) + matching ChromeDriver from Chrome for Testing
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget unzip ca-certificates fonts-liberation \
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb \
    && CHROME_VERSION=$(google-chrome --version | awk '{print $3}') \
    && echo "Installed Chrome $CHROME_VERSION" \
    && wget -q -O /tmp/chromedriver.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip -q /tmp/chromedriver.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/* /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py scraper.py summarizer.py ./

EXPOSE 7000

# API starts automatically when the container runs
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "--workers", "2", "--threads", "2", "--timeout", "180", "app:app"]
