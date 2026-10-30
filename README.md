# Lab Assignment 4 – Selenium News Summarizer API

- **Registration:** FA23-BDS-041
- **News source:** ARY News Pakistan (41 % 20 + 1 = 2)
- **Language:** Python (Selenium 4 + headless Google Chrome + ChromeDriver)

The container searches arynews.tv for a keyword with Selenium, opens the first result,
summarizes the article and returns JSON from `GET /get?keyword=...` on port 7000.

## Run
```bash
docker pull <dockerhub-username>/ary-news-api:v1
docker run -d -p 7000:7000 --name newsapi <dockerhub-username>/ary-news-api:v1
curl "http://localhost:7000/get?keyword=cricket"
```

## Response
```json
{"registration": "FA23-BDS-041", "newssource": "ARY News Pakistan",
 "keyword": "cricket", "url": "https://arynews.tv/...", "summary": "..."}
```

## Files
- `Dockerfile` – Python 3.11 + Google Chrome + ChromeDriver, starts the API automatically
- `scraper.py` – Selenium automation (search + article extraction)
- `summarizer.py` – extractive summarizer
- `app.py` – Flask REST API (`/` shows registration, `/get` returns JSON)
